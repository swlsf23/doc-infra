# Provision AWS hosting

This topic describes how you use **Terraform** in this repository to create **Amazon Web Services** resources for hosting the built static site: a private **Amazon S3** bucket, an **Amazon CloudFront** distribution in front of it, **origin access control (OAC)**, and a bucket policy that allows only that distribution to read objects. Hosting is **optional**; local builds do not require AWS.

Complete [Setup: environment](setup-environment.md) and the [AWS account checklist](aws-account-checklist.md) first. Terraform definitions live under `infra/terraform/` in your clone (see `infra/README.md` in the repository for how this fits with deploy automation and git hygiene).

::: note
`terraform apply` creates billable resources. Run **`terraform plan`** before every apply and tear down sandboxes you no longer need (`terraform destroy` when policy allows; you may need `force_destroy_bucket` in `terraform.tfvars` for non-empty buckets).
:::

## Configure variables

To set the inputs required by Terraform:

1. From the repository root, open the example variables file at:

    ```text
    infra/terraform/terraform.tfvars.example
    ```

1. Copy it to the path below (that file is gitignored):

    ```text
    infra/terraform/terraform.tfvars
    ```

Edit that file so assignments match your environment. The variables you set most often are the following (sample values illustrate HCL syntax only):

| Variable | Description | Sample value |
| --- | --- | --- |
| `site_bucket_name` | Globally unique S3 bucket name (DNS naming rules apply). | `"acme-corp-doc-infra-site-prod"` |
| `aws_region` | AWS Region for Regional resources (for example the bucket). | `"us-east-1"` |
| `name_prefix` | Short prefix for resource names and tags. | `"doc-infra"` |
| `force_destroy_bucket` | When `true`, `terraform destroy` can delete a non-empty bucket. Use `false` unless you accept data loss in that bucket. | `false` |
| `cloudfront_price_class` | CloudFront edge price class. Allowed values include `PriceClass_100`, `PriceClass_200`, and `PriceClass_All`. | `"PriceClass_100"` |

## Run Terraform

To create or update the infrastructure:

1. Open a terminal. From the repository root, change directory into the Terraform working directory:

    ```bash
    cd infra/terraform
    ```

1. Initialize the working directory and download providers:

    ```bash
    terraform init
    ```

1. Review the planned changes:

    ```bash
    terraform plan
    ```

1. Apply the configuration when the plan matches what you expect:

    ```bash
    terraform apply
    ```

Terraform prints **outputs** after a successful apply, including **`site_s3_bucket_name`**, **`cloudfront_distribution_id`**, and **`cloudfront_domain_name`**. You use the bucket name and distribution ID when you upload the site and invalidate the cache; you open the CloudFront domain name in a browser to verify content once objects are present.

## State and secrets

Terraform writes **state** locally unless you configure a remote **backend**. Do **not** commit real `terraform.tfvars`, state files, or secrets. The repository **`.gitignore`** lists patterns to keep those out of git.
