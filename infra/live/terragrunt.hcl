locals {
    s3_bucket_name = "terraform-state-lambda-cicd-us-east-1"
    region = "us-east-1"
}

remote_state {
    backend = "s3"

    config = {
        encrypt = true
        bucket = local.s3_bucket_name
        key    = "${path_relative_to_include()}/terraform.tfstate"
        region = local.region
        disable_aws_client_checksums = true
    }

    generate = {
        path = "backend.tf"
        if_exists = "overwrite_terragrunt"
    }
}