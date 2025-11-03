variable "allocated_storage" {
  description = "The allocated storage for the RDS instance."
  type        = number
}

variable "instance_class" {
  description = "The instance class for the RDS instance."
  type        = string
}

variable "db_username" {
  description = "The username for the RDS instance."
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "The password for the RDS instance."
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "The name of the RDS instance."
  type        = string
}
