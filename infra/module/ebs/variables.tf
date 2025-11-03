variable "availability_zone" {
  description = "The availability zone in which to create the EBS volume."
  type        = string
}

variable "size" {
  description = "The size of the EBS volume in gigabytes."
  type        = number
}

variable "type" {
  description = "The type of the EBS volume."
  type        = string
  default     = "gp3"
}

variable "tags" {
  description = "A map of tags to assign to the EBS volume."
  type        = map(string)
  default     = {}
}