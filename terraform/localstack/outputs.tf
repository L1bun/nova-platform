output "vpc_id" { value = aws_vpc.main.id }
output "public_subnet_ids" { value = aws_subnet.public[*].id }
output "private_subnet_ids" { value = aws_subnet.private[*].id }
output "gitops_bucket" { value = aws_s3_bucket.gitops.bucket }
output "tf_state_bucket" { value = aws_s3_bucket.tf_state.bucket }
output "eks_node_role_arn" { value = aws_iam_role.eks_node.arn }
output "app_service_role_arn" { value = aws_iam_role.app_service.arn }
