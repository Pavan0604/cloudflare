terraform {
  required_providers {
    github = {
      source = "integrations/github"
      version = "6.3.1"
    }
  }
}

provider "github" {
  token = "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"
}