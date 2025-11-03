resource "aws_ebs_volume" "ebs-volume" {
  availability_zone = var.availability_zone
  size              = var.size
  type              = var.type
  tags              = var.tags
}
