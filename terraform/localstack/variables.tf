variable "aws_region" {
  type    = string
  default = "us-east-1"
}
variable "environment" {
  type    = string
  default = "dev"
}
variable "team" {
  type    = string
  default = "platform-engineering"
}
variable "cost_center" {
  type    = string
  default = "CC-1000"
}
variable "vpc_cidr" {
  type    = string
  default = "10.42.0.0/16"
}
variable "public_subnet_cidrs" {
  type    = list(string)
  default = ["10.42.1.0/24", "10.42.2.0/24"]
}
variable "private_subnet_cidrs" {
  type    = list(string)
  default = ["10.42.11.0/24", "10.42.12.0/24"]
}
variable "availability_zones" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b"]
}
