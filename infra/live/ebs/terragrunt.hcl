include {
    path = find_in_parent_folders()
}

terraform {
    source = "../../module/ebs"
}

inputs = {
    availability_zone = "us-east-1a"
    size              = 20
    type              = "gp2"
    tags = {
        Name = "MyEBSVolume"
    }
}