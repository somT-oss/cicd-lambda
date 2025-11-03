resource "aws_db_instance" "database" {
  allocated_storage    = var.allocated_storage
  engine               = "mysql"
  engine_version       = "5.7"
  instance_class       = var.instance_class
  db_name                 = var.db_name
  username             = var.db_username
  password             = var.db_password
  parameter_group_name = "default.mysql5.7"
  skip_final_snapshot  = true
}
