terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# NexusOps VPC
resource "aws_vpc" "nexus_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = {
    Name        = "nexusops-vpc-prod"
    Environment = "production"
  }
}

# Production EKS Cluster for NexusOps Control Plane & Runners
resource "aws_eks_cluster" "nexus_eks" {
  name     = "nexusops-eks-production"
  role_arn = aws_iam_role.eks_cluster_role.arn
  version  = "1.28"

  vpc_config {
    subnet_ids              = [aws_subnet.private_1.id, aws_subnet.private_2.id]
    endpoint_private_access = true
    endpoint_public_access  = true
  }
}

# Encrypted S3 Bucket for Build Artifacts & Logs
resource "aws_s3_bucket" "artifacts" {
  bucket = "nexusops-artifacts-prod-vault"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts_encrypt" {
  bucket = aws_s3_bucket.artifacts.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
