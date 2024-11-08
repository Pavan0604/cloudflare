resource "github_repository" "gcp_testing_repo" {
  name        = "gcp-testing"
  description = "A new repository created with Terraform"
  visibility  = "public"
}

variable "GCP_CLEVERTAP_PRODUCT_INTELLIGENCE_PRIVATE_KEY" {
  type      = string
  sensitive = true
}

resource "github_actions_secret" "gcp_testing_repo-GCP_CLEVERTAP_PRODUCT_INTELLIGENCE_PRIVATE_KEY" {
  repository      = github_repository.gcp_testing_repo.name
  secret_name     = "GCP_CLEVERTAP_PRODUCT_INTELLIGENCE_PRIVATE_KEY"
  plaintext_value = var.GCP_CLEVERTAP_PRODUCT_INTELLIGENCE_PRIVATE_KEY
}