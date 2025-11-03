include {
    path = find_in_parent_folders()
}

terraform {
    source = "../../module/ec2"
}

inputs = {
    ami = "ami-0bdd88bd06d16ba03"
    instance_type = "t2.micro"
    vpc_cidr_block = "10.0.0.0/16"
    subnet_cidr_block = "10.0.0.0/24"
}

