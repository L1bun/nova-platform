#!/usr/bin/env python3
"""nova - NovaPlatform self-service environment CLI."""

import subprocess
from pathlib import Path

import typer

app = typer.Typer(help="NovaPlatform self-service environment CLI")
env_app = typer.Typer(help="Manage NovaPlatform environments")
infra_app = typer.Typer(help="Manage NovaPlatform's LocalStack-backed infrastructure via Terraform")
app.add_typer(env_app, name="env")
app.add_typer(infra_app, name="infra")

GITOPS_REPO = Path("/mnt/d/nova-platform-gitops")
TERRAFORM_DIR = Path("/mnt/d/nova-platform/terraform/localstack")

RBAC_TEMPLATE = """apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: team-edit
  namespace: {name}
rules:
  - apiGroups: ["", "apps", "batch"]
    resources: ["pods", "deployments", "replicasets", "services", "configmaps", "jobs", "cronjobs"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {name}-team-sa
  namespace: {name}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {name}-team-binding
  namespace: {name}
subjects:
  - kind: ServiceAccount
    name: {name}-team-sa
    namespace: {name}
roleRef:
  kind: Role
  name: team-edit
  apiGroup: rbac.authorization.k8s.io
"""

VALUES_TEMPLATE = "replicaCount: 1\nimage:\n  repository: nginxdemos/hello\n  tag: plain-text\n"

APPLICATION_TEMPLATE = """apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: nova-platform-{name}
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/L1bun/nova-platform-gitops.git
    targetRevision: main
    path: charts/web-service
    helm:
      valueFiles:
        - ../../environments/{name}/web-service-values.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: {name}
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
"""


def run(cmd, input_text=None, check=True):
    typer.echo(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, input=input_text, capture_output=True, text=True)
    if result.stdout.strip():
        typer.echo(result.stdout.strip())
    if result.returncode != 0:
        typer.echo(result.stderr.strip(), err=True)
        if check:
            raise typer.Exit(code=result.returncode)
    return result


@env_app.command("create")
def create(name: str):
    """Create a new environment: namespace, RBAC, and a GitOps-driven deployment."""
    typer.echo(f"Creating environment '{name}'...")

    ns_yaml = run(["kubectl", "create", "namespace", name, "--dry-run=client", "-o", "yaml"]).stdout
    run(["kubectl", "apply", "-f", "-"], input_text=ns_yaml)
    run(["kubectl", "label", "namespace", name, "managed-by=nova-cli", "--overwrite"])

    rbac_path = Path(f"/tmp/nova-rbac-{name}.yaml")
    rbac_path.write_text(RBAC_TEMPLATE.format(name=name))
    run(["kubectl", "apply", "-f", str(rbac_path)])

    env_dir = GITOPS_REPO / "environments" / name
    env_dir.mkdir(parents=True, exist_ok=True)
    (env_dir / "web-service-values.yaml").write_text(VALUES_TEMPLATE)

    run(["git", "-C", str(GITOPS_REPO), "add", "."])
    run(["git", "-C", str(GITOPS_REPO), "commit", "-m", f"nova: add environment {name}"], check=False)
    run(["git", "-C", str(GITOPS_REPO), "push"])

    app_path = Path(f"/tmp/nova-app-{name}.yaml")
    app_path.write_text(APPLICATION_TEMPLATE.format(name=name))
    run(["kubectl", "apply", "-f", str(app_path)])

    typer.echo(f"Environment '{name}' created.")


@env_app.command("destroy")
def destroy(name: str):
    """Tear down an environment: Argo CD Application and namespace."""
    typer.echo(f"Destroying environment '{name}'...")
    run(["kubectl", "delete", "application", f"nova-platform-{name}", "-n", "argocd"], check=False)
    run(["kubectl", "delete", "namespace", name], check=False)
    typer.echo(
        f"Environment '{name}' destroyed. "
        f"GitOps values under environments/{name}/ were left in git for audit history."
    )


@env_app.command("list")
def list_envs():
    """List all environments managed by nova."""
    run(["kubectl", "get", "namespaces", "-l", "managed-by=nova-cli"], check=False)


@env_app.command("status")
def status(name: str):
    """Show status of a specific environment."""
    typer.echo(f"--- Namespace: {name} ---")
    run(["kubectl", "get", "pods", "-n", name], check=False)
    typer.echo(f"--- Argo CD Application: nova-platform-{name} ---")
    run(["kubectl", "get", "application", f"nova-platform-{name}", "-n", "argocd"], check=False)


@infra_app.command("plan")
def infra_plan():
    """Show the Terraform plan for the LocalStack-backed infra layer."""
    run(["terraform", f"-chdir={TERRAFORM_DIR}", "plan"], check=False)


@infra_app.command("apply")
def infra_apply():
    """Apply the Terraform-managed infra layer (VPC/S3/IAM on LocalStack)."""
    run(["terraform", f"-chdir={TERRAFORM_DIR}", "apply", "-auto-approve"], check=False)


if __name__ == "__main__":
    app()
