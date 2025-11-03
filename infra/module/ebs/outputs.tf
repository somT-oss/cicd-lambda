output "id" {
  description = "The ID of the EBS volume."
  value       = aws_ebs_volume.ebs-volume.id
}

output "arn" {
  description = "The ARN of the EBS volume."
  value       = aws_ebs_volume.ebs-volume.arn
}

output "size" {
  description = "The size of the EBS volume."
  value       = aws_ebs_volume.ebs-volume.size
}

output "availability_zone" {
  description = "The availability zone of the EBS volume."
  value       = aws_ebs_volume.ebs-volume.availability_zone
}
