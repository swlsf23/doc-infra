# Provision AWS hosting

This topic describes how you use **Terraform** in this repository to create **Amazon Web Services** resources for hosting the built static site: a private **Amazon S3** bucket, an **Amazon CloudFront** distribution in front of it, **origin access control (OAC)**, and a bucket policy that allows only that distribution to read objects. Hosting is **optional**. Local builds do not require AWS.

Complete [Setup: environment](setup-environment.md) and the [AWS account checklist](aws-account-checklist.md) first. Terraform definitions live under `infra/terraform/` in your clone (see `infra/README.md` in the repository for how this fits with deploy automation and git hygiene). For a hostname under a domain you already own (for example **`docs.example.com`**), read [Custom domain requirements](custom-domain-requirements.md) for **DNS**, **TLS**, and **CloudFront** prerequisites with links to **AWS** documentation.

The sections below follow this order:

- Configure variables
- Authenticate for Terraform
- Run Terraform
- After apply
- Troubleshooting
- State and secrets

::: note
`terraform apply` creates billable resources. Run **`terraform plan`** before every apply and tear down sandboxes you no longer need (`terraform destroy` when policy allows. You may need `force_destroy_bucket` in `terraform.tfvars` for non-empty buckets).
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

1. Edit `terraform.tfvars` so each assignment matches your environment. Use the table below for meaning and for valid HCL shapes (sample values are illustrations only).

| Variable | Description | Sample value |
| --- | --- | --- |
| `site_bucket_name` | Globally unique S3 bucket name (DNS naming rules apply). | `"acme-corp-doc-infra-site-prod"` |
| `aws_region` | AWS Region for Regional resources (for example the bucket). | `"us-east-1"` |
| `name_prefix` | Short prefix for resource names and tags. | `"doc-infra"` |
| `force_destroy_bucket` | When `true`, `terraform destroy` can delete a non-empty bucket. Use `false` unless you accept data loss in that bucket. | `false` |
| `cloudfront_price_class` | CloudFront edge price class. Allowed values include `PriceClass_100`, `PriceClass_200`, and `PriceClass_All`. | `"PriceClass_100"` |

## Authenticate for Terraform

Before **`terraform plan`** or **`terraform apply`**, you must have **AWS credentials** available in the environment where you run Terraform. Terraform’s **AWS provider** uses the same **default credential chain** as the **AWS Command Line Interface (AWS CLI)** (shared config files, environment variables, and related sources). There is no separate Terraform sign-in.

If you skip the steps below, **`terraform plan`** often fails with **No valid credential sources found** or text about **EC2 IMDS** or **GetMetadata**. That happens because the provider looks for **EC2** instance metadata after other sources are empty. On a laptop there is no instance role there, so the message really means **no usable credentials in this shell** (including an expired **SSO** session). Finish this section before you blame **Terraform** or **IMDS**.

Run Terraform from a **terminal on your own machine** (or any environment where you already run `aws` for deploys) so interactive prompts, **IAM Identity Center** (AWS SSO) refresh, and profile selection behave the way you expect.

To authenticate this terminal for Terraform:

1. Sign in to **IAM Identity Center** using the command that matches your **`~/.aws/config`**. Run **one** of the following (not both).

    When your profile references **`sso_session`** and a matching **`[sso-session …]`** block exists in the same file:

    ```bash
    aws sso login --sso-session your-session-name
    ```

    When your team uses **`aws sso login`** with a **named profile** instead:

    ```bash
    aws sso login --profile your-profile-name
    ```

1. When **`aws configure list`** shows **`<not set>`** for the unnamed default profile, you are not using **default** credentials. Export the same **named profile** you use for **`aws`** deploys for this terminal session:

    ```bash
    export AWS_PROFILE=your-profile-name
    ```

1. Verify which principal the CLI resolves:

    ```bash
    aws sts get-caller-identity
    ```

    The **`Arn`** field names the caller. Values containing **`assumed-role`** usually mean a **role** session (typical with SSO or role chaining). Values ending with **`user/...`** mean an **IAM user** session. Either works when **IAM** policies allow creating the resources in this module.

    If the command prints **token** **expired**, **refresh failed**, or similar while you use a profile backed by **IAM Identity Center**, your **SSO** session is stale. Run **`aws sso login`** again with the same **`--profile`** or **`--sso-session`** argument you use for a fresh login, then run **`aws sts get-caller-identity`** again until it succeeds.

1. Keep using **this same terminal session** for **`terraform init`**, **`terraform plan`**, and **`terraform apply`**. A new window drops **`AWS_PROFILE`** and any in-memory session context unless you configure it again.

## Run Terraform

To create or update the infrastructure after you finish **Authenticate for Terraform** in the same terminal session:

1. From the repository root, change directory into the Terraform working directory:

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

## After apply

To capture the values Terraform created for later deploy steps:

1. Read the **Outputs** section printed at the end of **`terraform apply`**. It lists **`site_s3_bucket_name`**, **`cloudfront_distribution_id`**, and **`cloudfront_domain_name`**.

1. Any time later, from `infra/terraform/`, print the same values from state:

    ```bash
    terraform output
    ```

    You use the **bucket name** and **distribution ID** when you upload the built site to **S3** and when you invalidate **CloudFront**. You use the **CloudFront domain name** as the public **HTTPS** hostname until you attach a custom domain.

## Troubleshooting

Most early **`terraform plan`** failures are still **authentication** problems (wrong shell, **`AWS_PROFILE`** not set when you only have named profiles, or an expired **SSO** session). **Authenticate for Terraform** is written to prevent that. If you already followed it and still see **No valid credential sources** or **IMDS** wording, repeat that section from **`aws sso login`** through **`aws sts get-caller-identity`** in the **same** terminal where you run **`terraform`**.

If **`apply`** fails because the **S3** bucket name is already taken globally, change **`site_bucket_name`** in **`terraform.tfvars`** and run **`terraform plan`** again.

## State and secrets

To keep **Terraform** state and secrets off the remote and out of version control:

1. Expect **`terraform.tfstate`** and related state files in **`infra/terraform/`** while you use the default local **backend**. Do **not** add them to **git**. The repository **`.gitignore`** already lists common state file patterns.

1. Do **not** commit **`terraform.tfvars`** with real values. Only **`terraform.tfvars.example`** belongs in the repository as a template.

1. When more than one person or pipeline runs **Terraform** against the same infrastructure, configure a **remote backend** (for example **S3** plus **DynamoDB** locking) using **HashiCorp** documentation. That change is outside this topic’s minimal path.
