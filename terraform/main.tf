terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.6.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
}

# Criação do Data Lake (Google Cloud Storage)
resource "google_storage_bucket" "data-lake-bucket" {
  name          = var.gcs_bucket_name
  location      = var.location
  force_destroy = true # Facilita a exclusão do projeto após o curso

  storage_class = var.gcs_storage_class

  lifecycle_rule {
    condition {
      age = 30 # Apaga arquivos mais velhos que 30 dias (opcional, bom para economizar)
    }
    action {
      type = "Delete"
    }
  }
}

# Criação do Data Warehouse (BigQuery Dataset)
resource "google_bigquery_dataset" "dataset" {
  dataset_id                 = var.bq_dataset_name
  location                   = var.location
  delete_contents_on_destroy = true # Cuidado em prod, mas útil para projetos de estudo
}