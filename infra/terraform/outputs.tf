output "site_s3_bucket_name" {
  description = "S3 bucket name: sync target for the static site (for example output/site/)."
  value       = aws_s3_bucket.site.id
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID: use for cache invalidation after deploy."
  value       = aws_cloudfront_distribution.site.id
}

output "cloudfront_domain_name" {
  description = "CloudFront HTTPS hostname (*.cloudfront.net) until a custom domain is configured."
  value       = aws_cloudfront_distribution.site.domain_name
}
