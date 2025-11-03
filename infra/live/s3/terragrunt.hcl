include {
    path = find_in_parent_folders()
}

terraform {
    source = "../../module/s3"
}

inputs = {
    bucket_name = "my-terragrunt-s3-bucket-956843"
}
