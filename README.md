# AWS Cost Optimizer

> An automated infrastructure analysis tool that identifies cost optimization opportunities across AWS resources using Lambda functions, CloudFormation, and CI/CD pipelines.

![AWS](https://img.shields.io/badge/AWS-Cloud-orange)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![SAM](https://img.shields.io/badge/AWS-SAM-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [CI/CD Pipeline](#cicd-pipeline)
- [What I Learned](#what-i-learned)

## Overview

AWS Cost Optimizer is a serverless application that automatically scans your AWS infrastructure to identify cost optimization opportunities. It analyzes EC2 instances, RDS databases, EBS volumes, and S3 buckets, generating detailed reports on potential savings.

### Key Benefits

-  **Cost Reduction**: Identify underutilized resources and potential savings
-  **Automated Scanning**: Scheduled daily analysis via EventBridge
-  **Detailed Reporting**: Store findings in DynamoDB for historical tracking
-  **Serverless**: No infrastructure to manage
-  **Secure**: IAM least-privilege access policies

## Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS Cost Optimizer                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐      ┌──────────────────────────────────────┐
│   EventBridge    │─────▶│         Lambda Functions             │
│  (Daily Cron)    │      │  ┌────────────────────────────────┐  │
└──────────────────┘      │  │  • ec2-analyzer               │  │
                          │  │  • rds-analyzer               │  │
                          │  │  • ebs-analyzer               │  │
                          │  │  • s3-analyzer                │  │
                          │  └────────────────────────────────┘  │
                          └──────────────┬───────────────────────┘
                                         │
                          ┌──────────────▼───────────────────────┐
                          │          DynamoDB Table              │
                          │     (CostOptimizerFindings)          │
                          │  ┌────────────────────────────────┐  │
                          │  │  id (HASH)                     │  │
                          │  │  timestamp (RANGE)             │  │
                          │  │  resource_type, metadata, etc. │  │
                          │  └────────────────────────────────┘  │
                          └──────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         CI/CD Pipeline                           │
└─────────────────────────────────────────────────────────────────┘

GitHub ──▶ CodePipeline ──▶ CodeBuild ──▶ CloudFormation ──▶ Lambda
           │                 │               (SAM Deploy)
           │                 │
           │                 └──▶ S3 Artifacts
           │
           └──▶ Webhook (Auto-trigger on push)
```

### Component Details

#### Lambda Functions

| Function | Purpose | Checks |
|----------|---------|--------|
| **ec2-analyzer** | Analyzes EC2 instances | Running instances, CPU utilization, network traffic |
| **rds-analyzer** | Analyzes RDS databases | Running instances with >10GB storage |
| **ebs-analyzer** | Analyzes EBS volumes | All volumes (attached/unattached), I/O metrics |
| **s3-analyzer** | Analyzes S3 buckets | Bucket size, object count, storage classes, public access |

#### Supporting Services

- **DynamoDB**: Stores analysis findings with partition key (`id`) and sort key (`timestamp`)
- **EventBridge**: Triggers analyzers daily at 2 AM UTC (`cron(0 2 * * ? *)`)
- **CloudWatch**: Collects metrics for CPU, network, IOPS, and storage
- **IAM**: Provides least-privilege roles for Lambda execution
- **S3**: Stores CodePipeline artifacts and SAM deployment packages

## Features

- **Automated Resource Analysis**
  - EC2 instances (running status, metrics)
  - RDS databases (storage >10GB)
  - EBS volumes (attachment status, I/O)
  - S3 buckets (size, versioning, lifecycle)

- **Metrics Collection** (7-day averages)
  - CPU utilization
  - Network traffic
  - Database connections
  - Storage I/O operations
  - S3 request counts

- **Data Storage**
  - Historical tracking in DynamoDB
  - Timestamped records
  - Queryable findings

- **CI/CD Pipeline**
  - Automated testing
  - Multi-stage deployment (dev/prod)
  - CloudFormation stack management
  - Artifact versioning


## CI/CD Pipeline

### Pipeline Architecture

```
┌─────────┐    ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ GitHub  │───▶│ CodePipeline│───▶│  CodeBuild   │───▶│CloudFormation│
│  Push   │    │   Source    │    │    Build     │    │   Deploy    │
└─────────┘    └─────────────┘    └──────────────┘    └─────────────┘
                                          │
                                          ▼
                                   ┌─────────────┐
                                   │ S3 Artifacts│
                                   └─────────────┘
```

### Pipeline Stages

1. **Source**: GitHub webhook triggers on push to `main`
2. **Build**: CodeBuild runs tests and packages Lambda functions
3. **Deploy-Dev**: CloudFormation deploys to dev environment


## What I Learned

### 1. DevOps Best Practices for CI/CD Pipelines in AWS

- **Infrastructure as Code**: Managed all resources via CloudFormation/SAM templates
- **Automated Testing**: Integrated pytest in build phase for quality assurance
- **Multi-stage Deployments**: Implemented dev/prod environments with manual approval gates
- **Artifact Management**: Versioned deployments using S3 artifact buckets
- **GitOps Workflow**: Automated deployments triggered by Git commits


### 2. Building and Managing Lambda Deployments

**CodeBuild Integration:**
- Configured buildspec.yml for automated builds
- Managed Python dependencies across multiple Lambda functions
- Handled build artifacts and deployment packages

**S3 for Artifacts:**
- Stored Lambda deployment packages in versioned S3 buckets
- Managed artifact lifecycle policies (30-day retention)
- Used S3 paths in CloudFormation for Lambda code references

**AWS SAM (Serverless Application Model):**
- Simplified Lambda function definitions with SAM syntax
- Used `sam build` to package functions with dependencies
- Leveraged `sam package` to upload artifacts to S3
- Deployed with `sam deploy` for stack creation/updates

**Challenges Overcome:**
- Empty zip file deployments → Restructured my folder structure to match the CodeUri format in the SAM template
- Build caching → Implemented proper artifact handling in buildspec

### 3. Deploying CloudFormation Stacks

**Stack Management:**
- Created, updated, and deleted stacks via CLI and CodePipeline
- Used change sets for safe production deployments
- Implemented stack parameters for environment-specific configuration

### 4. Setting Up Infrastructure Using CloudFormation

**Resources Deployed:**
- DynamoDB tables with partition and sort keys
- Lambda functions with IAM roles and policies
- EventBridge rules for scheduled execution
- S3 buckets with lifecycle policies
- IAM roles with least-privilege policies

### 5. Setting Up Dummy Resources with Terraform/Terragrunt

**Testing Infrastructure:**
- Created mock EC2 instances, RDS databases, and S3 buckets for testing
- Used Terraform modules for reusable resource definitions
- Managed multiple environments with Terragrunt

**Terragrunt Benefits:**
- DRY (Don't Repeat Yourself) configuration
- Environment-specific variable management
- Remote state management in S3
- Dependency management between modules