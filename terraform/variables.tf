variable "project" {
  description = "Project ID no GCP"
  type        = string
}

variable "region" {
  description = "Região principal do projeto"
  type        = string
}

variable "location" {
  description = "Localização dos recursos"
  type        = string
}

variable "bq_dataset_name" {
  description = "Nome do Dataset no BigQuery"
  type        = string
}

variable "gcs_bucket_name" {
  description = "Nome do Bucket no GCS (Deve ser único globalmente!)"
  type        = string
}

variable "gcs_storage_class" {
  description = "Classe de armazenamento do Bucket"
  type        = string
}