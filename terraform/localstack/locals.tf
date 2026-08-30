locals {
  name_prefix = "nova-platform-${var.environment}"
  common_tags = {
    Project     = "NovaPlatform"
    Team        = var.team
    Environment = var.environment
    CostCenter  = var.cost_center
    ManagedBy   = "terraform"
  }
}
