variable "project" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "Primary project region"
  type        = string
}

variable "location" {
  description = "Resource location"
  type        = string
}

variable "bq_dataset_name" {
  description = "BigQuery Dataset name"
  type        = string
}

variable "gcs_bucket_name" {
  description = "GCS Bucket name (must be globally unique!)"
  type        = string
}

variable "gcs_storage_class" {
  description = "Bucket storage class"
  type        = string
}