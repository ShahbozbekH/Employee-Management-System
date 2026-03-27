# variables.tf

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_prefix" {
  description = "Prefix for all resources"
  type        = string
  default     = "student"
}

variable "frontend_bucket_name" {
  description = "S3 bucket name for frontend hosting"
  type        = string
  default     = "student-frontend-bucket-sh"
}

variable "ec2_instance_type" {
  description = "EC2 instance type for backend and MongoDB"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "EC2 Key Pair name for SSH access"
  type        = string
  default     = "student-employee-management-sh"
}

variable "backend_ami" {
  description = "AMI ID for backend EC2 instance (Ubuntu recommended)"
  type        = string
  default     = "ami-0ec10929233384c7f"
}
