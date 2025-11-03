include {
    path = find_in_parent_folders()
}

terraform {
    source = "../../module/rds"
}

inputs = {
    allocated_storage = 10
    instance_class    = "db.t2.micro"
    db_username       = "admin"
    db_password       = "password123"
    db_name = "test"
}