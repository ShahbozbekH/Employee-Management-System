# outputs.tf

output "s3_bucket_name" {
  description = "Name of the S3 bucket for frontend hosting"
  value       = aws_s3_bucket.frontend_bucket.id
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.frontend_distribution.domain_name
}

output "ec2_public_ip" {
  description = "Public IP of the backend EC2 instance"
  value       = aws_instance.backend_instance.public_ip
}
