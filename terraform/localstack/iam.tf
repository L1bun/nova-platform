data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "eks_node" {
  name               = "${local.name_prefix}-eks-node-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json
  tags               = local.common_tags
}

resource "aws_iam_role_policy_attachment" "eks_node_worker" {
  role       = aws_iam_role.eks_node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

data "aws_iam_policy_document" "app_s3_access" {
  statement {
    actions   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
    resources = [aws_s3_bucket.gitops.arn, "${aws_s3_bucket.gitops.arn}/*"]
  }
}

resource "aws_iam_policy" "app_s3_access" {
  name   = "${local.name_prefix}-app-s3-access"
  policy = data.aws_iam_policy_document.app_s3_access.json
  tags   = local.common_tags
}

resource "aws_iam_role" "app_service" {
  name               = "${local.name_prefix}-app-service-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json
  tags               = local.common_tags
}

resource "aws_iam_role_policy_attachment" "app_service_s3" {
  role       = aws_iam_role.app_service.name
  policy_arn = aws_iam_policy.app_s3_access.arn
}
