variable "aws_region" {
  type        = string
  description = "AWS Region where Regional resources (for example the S3 bucket) are created."
}

variable "site_bucket_name" {
  type        = string
  description = "Globally unique S3 bucket name for static site objects (DNS naming rules apply)."
}

variable "name_prefix" {
  type        = string
  description = "Short prefix for resource names and tags."
  default     = "doc-infra"
}

variable "force_destroy_bucket" {
  type        = bool
  description = "When true, allows terraform destroy to delete the bucket even if it contains objects. Use false in production."
  default     = false
}

variable "cloudfront_price_class" {
  type        = string
  description = "CloudFront price class: PriceClass_All, PriceClass_200, or PriceClass_100."
  default     = "PriceClass_100"
}
