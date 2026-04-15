# Infrastructure (AWS)

This directory documents **optional** hosting for the static site produced by doc-infra. The goal is a **fork-friendly** setup: anyone cloning the repo can provision their own AWS resources and deploy without this project shipping account IDs, secrets, or fixed bucket names.

Nothing here is required to **build** the site locally. That is still: manifest → convert → `build_site` (see the [root README](../README.md)).

## What we are implementing

| Piece | Purpose |
| --- | --- |
| **`terraform/`** (planned) | Terraform **root module**: private **S3** bucket for static files, **CloudFront** distribution in front of it, **Origin Access Control (OAC)** so the bucket stays private (no public bucket ACLs), and an S3 bucket policy that only allows CloudFront to read objects. |
| **Deploy script** (planned, e.g. `../scripts/deploy-site-to-s3.sh`) | Upload the built site with `aws s3 sync`, set sensible **Cache-Control** for HTML entrypoints where needed, then **invalidate** the CloudFront distribution so visitors see new content quickly. |
| **GitHub Actions** (planned, `.github/workflows/deploy.yml`) | On push to `main` (and manual runs), install Python dependencies, run the three build commands, assume an IAM role via **OIDC** (no long-lived AWS keys in GitHub), then run the deploy script. |

**Baseline (phase 1):** use the **default CloudFront HTTPS URL** (`*.cloudfront.net`). **Custom domain, ACM certificate, and Route 53** are optional later enhancements so a minimal fork works without DNS.

**OSS hygiene:** real `terraform.tfvars`, state files, and overrides stay **out of git** (see `.gitignore`). Only a **`terraform.tfvars.example`** (or similar) with placeholders is committed.

## Deploy artifact

The upload target is whatever **`site_output_dir`** points to in [`code/config.yml`](../code/config.yml). The default is **`output/site/`** (gitignored as part of `output/`).

Build pipeline (from repository root, with Python 3.11+ and `pip install -r requirements.txt`):

```bash
python code/generate_manifest.py
python code/convert.py
python code/build_site.py
```

Then sync **`output/site/`** to S3 and invalidate CloudFront (once the deploy script exists).

## Terraform outputs (intended)

After `terraform apply`, you should copy values for local or CI deploy:

- **S3 bucket name** — sync target for the static site.
- **CloudFront distribution ID** — for cache invalidation after deploy.
- **CloudFront domain name** — browser URL until a custom domain is configured.
- **`github_actions_deploy_role_arn`** (when GitHub OIDC is enabled) — set as the **`AWS_ROLE_ARN`** secret in GitHub for Actions.

Exact output names will match the Terraform module once it is added.

## GitHub Actions configuration (intended)

Forks that enable the workflow will set:

| Kind | Name | Purpose |
| --- | --- | --- |
| Secret | `AWS_ROLE_ARN` | IAM role ARN from Terraform (OIDC trust for GitHub). |
| Variable | `SITE_S3_BUCKET` | S3 bucket name. |
| Variable | `CLOUDFRONT_DISTRIBUTION_ID` | Distribution ID for invalidation. |
| Variable | `AWS_REGION` | Optional; default region for the AWS CLI. |

The workflow should use **concurrency** so only one deploy runs at a time per branch, with **cancel-in-progress** so an older run cannot overwrite S3 after a newer push.

## Optional: GitHub OIDC in Terraform

Terraform may create an IAM **OIDC** trust for `token.actions.githubusercontent.com`, scoped to a **repository** variable (e.g. `owner/repo`) and branch. If your AWS account already has a GitHub OIDC provider, you may need to **import** it into Terraform once; that will be documented in `terraform/` when implemented.

## Forking this repository

1. Clone your fork and follow the [root README](../README.md) to build locally.
2. Install [Terraform](https://www.terraform.io/) (>= 1.5) and configure AWS credentials (e.g. `aws configure sso` or environment variables).
3. Copy `terraform.tfvars.example` to `terraform.tfvars`, set a **globally unique** bucket name and your AWS settings; set `github_repository` if you use OIDC.
4. Run `terraform init`, `terraform plan`, `terraform apply` under `infra/terraform/` (once present).
5. Configure GitHub **Secrets** and **Variables** if you use Actions, or deploy from your machine using the deploy script and the same bucket and distribution ID.
