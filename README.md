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
> ```markdown
> ![Architecture Diagram](https://viewer.diagrams.net/index.html?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=serverless-service-checker.drawio.png&dark=auto#R%3Cmxfile%3E%3Cdiagram%20name%3D%22Page-1%22%20id%3D%22NIwX1alYsEJmuM7UA1jZ%22%3E7Vxtc5s4EP41%2BZgMQrzYH%2BOXtHeTzmSazvTuUwYb2dYVIwpyYvfXnwSSjZAcSAN20tAmE7QSQuw%2Bu5IerX0Bx%2BvtpzRIVl9IiKIL2wq3F3ByYdue5VnsD5fsCgn0fSFZpjgsZOAguMe%2FkBDKZhscokxpSAmJKE5U4ZzEMZpTRRakKXlSmy1IpD41CZZIE9zPg0iXfschXRXSgWsd5J8RXq7kk4ElataBbCwE2SoIyVNJBKcXcJwSQour9XaMIq49qZfivpsjtfuBpSimTW542NLMs%2FDP2d8LfJOsv%2Bxuv%2BNL4BTdPAbRRryxGC3dSRUsU7JJRDOUUrQ1KT6YyeaWPjCwf10GFETWiKY71kR0dAmkNiVIZPnpoHHgSMWuSur2JL4CYeblvveDJtiFUMZLFFOvl%2BwHonM%2BPOsCjhKCY5oPwh2xHzascfHrsqZjLrmyXYPQJPN1IdCbsT%2FA9ISq0CTzdSHQm%2FGSHLUqNMl8Vx9x9W5guBtU7mY%2FcEQ2NMIxGu%2B9mut4QWI6JhFJc%2F1D9v%2BGW3S0wFFUko%2BHtjsBTJ7RlPxApZpF%2Fo%2FVhEG2QqHoloMaM4%2B%2FDWYouiMZppjErG5GKCXrUoPrCC95BSUJkwaiNGcwR%2BwBoxVdM4jlT%2BYjFbEM2LIskMMfGWRJ8VoLvOXjGLHgkPDK9XbJA%2BlV8JQ5VynKyCado7%2FmfDwjViyu1FZzFnQTnCCuL9bqqKOWHfKZWKC7ackL%2FYHug1LWugvCehdkkSkO94Z8WmGK7pNgzmufmIYqRinBJCYdKWunTl%2B1Ecx1u4pgvqYtFLKpTRRJSldkSeIgmh6kI1Wfhza3hEM%2B1%2BJ%2FiNKdwHawoUTVcfFM%2FqDfUScbbQ74Zxq6Yg0QpEv0XIee2TwpigKKH9XRta56tx65SgQyRruSVrVQE1VC1b7iN2NZNfw8oRlmoSa7WmK62sxYCyYPMVLi7%2BRmMp1M23ch2Q1QVwVgYPApz%2BBS%2B4at23X4R7qU19ClBud0Ka9fj%2FXrsXezHpttMN9ndrC%2B2O%2Bs1eBoW8YFhyE4Ol0Fx0Hvob2HvhsPZXumiOy6dFFguU181DH5qNMVq2EZnNSLKNdnEsSKt3o%2FN5yayi1xmeWmuWYNXCfZ5mqT9exqyf9%2BwvQzWyqK7tjwih6LSi0UMG3TmkVuFURrHIbFkgqx4QjCSY8k3Bn4KioTaNJgLfZ%2Bhu1g0U7yfMNu0VHhvDwDOIaGAN7Z4haYKK%2BWsHH9%2FZ5Vj5nfjfKZsQdJI5A4nquCRAaGEkgccFKQ2KcAyaQIzj1KGqFkaDVAiWmj3B1KTNRd6yi5k6Rnj5OG0USdclwDoeIMTooTTzPS2yBUhKiWOgFN6UhotsxpuBPQgI%2BUy%2BlgTjk867j0RiCtOfZznAoeTUsg27SH7ezUD75Vhq8pIJ2mZB50z4lIafn3q%2BdhQz2D4Vn1DM%2BhZ6bNdPcPv%2F%2FKlcV%2FRXd5YbJVSjtRajMwDxraxz4yZ54oMvek2VlJs16db4aDnPrA9Ucfh4OMyCZckHQdFONuY0V1yDCQKyrH1ldUxiPT7vKohvURzgibro1tsB28CndxsCYP4UzHpz314WhwoZ%2BEvySVpMZ%2B0Fftdwn1FbFtWhHv803aXxE3yMLpOkEQ%2BBUeDBjZUtvEhLnDrjRjN0idPF9%2BEjyy46xVmNPZbl8a%2Fn2EgihYz8LgYbGJ5yJCVwLCjTtwofPKgPAi24luBmqQ2G%2BRy6Z1TUG%2Bs1Qz%2BWa9ZV9nWTh8e6Y1Ef69aV9sWq%2FqtaYM0RObtsHU3pu23rTDNxiQTYxvWwcwcRBHu1%2FMaLZ1mxuFXdwIs2T9YUzDUF%2FdqhnigW9a6ne3PDOlWLaEma%2BTe3YZrLnnx7MsKarMQCnEIX6sitpArgDus49mYuXpPXJV5FY%2FrWVIa7KhKdx1lnpo%2B91Bdzq6r8HLLO3B%2B17A6zlvD7ymM4C2wDu2e%2FD%2BMeAdVhNKh%2BcHr4nebQk097DH7h%2BDXefNQRc6mpHeVw5C0yNucNYPbjngHGoupSDY58pBgE2Tw86bgwCbZIf1OQj9ofn5D83RIxvALMW5d3Zy4gosw8mi%2BcjV7mpicnT%2FO2XEBEq4PGRwHQmYeekOpZi9PMdG21FUHrO%2B9Uw702lwW7s4DvtRAfsPSK%2FWuXD1ewJMe3p4UirVMfFR73qt2Tif0nntF2%2BIW%2B846EpWdiqHLL5lq30UryBuO9ivvqdDyJddFS%2BpdZVDYf9Kr0CHTvh84%2B5qQkg%2BUXfnyEf9r0nSzjPQP570zyYU4ALFAPK7tn4XIpVu5B1kschQNwbs8KRkzPMCb%2FZ5gRrT8Q2tE6amfiLQJwK7kj3hG47UjJ%2BW7I5jkITdR5wIXrscaxi%2B9zmur58IquuBrueBDrnTSZ7IOjl%2ByvpxwwSEajKpbUjXgKavautsuSjnwxIQvqJlHv4rZjJSLxrtUqVcNLpFpVo0GqNKYWj0hUqkaFxLlZDRWBuV2NG4lSoBo7E0z1InR9J%2FStA25eHW0RhsQUQD9qxU9JFbAqX51izbt4miIMnwwRVSNN%2BkGYt2X5HAv3WMASmSqPnwTcxHXvuQFqgw0D2Wde1ce2Y3ep7TidBCRJw5jpe3eWkCDRwUcPzp6LrMKLX1QVC7cq51CQ2nA3Bg8snDh5pf4JWsePja3SKaH769GE7%2FBw%3D%3D%3C%2Fdiagram%3E%3C%2Fmxfile%3E#%7B%22pageId%22%3A%22NIwX1alYsEJmuM7UA1jZ%22%7D)
> ```

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