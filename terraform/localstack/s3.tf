resource "aws_s3_bucket" "gitops" {
  bucket = "${local.name_prefix}-gitops-artifacts"
  tags = merge(local.common_tags, {
    Name    = "${local.name_prefix}-gitops-artifacts"
    Purpose = "gitops-manifests-and-helm-artifacts"
  })
}

resource "aws_s3_bucket" "tf_state" {
  bucket = "${local.name_prefix}-tf-state"
  tags = merge(local.common_tags, {
    Name    = "${local.name_prefix}-tf-state"
    Purpose = "terraform-remote-state"
  })
}

resource "aws_s3_bucket_versioning" "tf_state" {
  bucket = aws_s3_bucket.tf_state.id
  versioning_configuration {
    status = "Enabled"
  }
}
