# AWS account checklist

Use this checklist before you provision **Amazon Web Services** resources for doc-infra (for example with Terraform). It does not replace your organization’s security or procurement rules; it collects the decisions and guardrails that usually block a first successful deploy when they are missing.

Install the **AWS Command Line Interface (AWS CLI)** first if you have not already done so (see [Setup: environment](setup-environment.md)).

::: Note
If your company uses **AWS Organizations**, **Control Tower**, or mandatory **IAM Identity Center**, complete their onboarding first. The items below assume you can sign in and obtain credentials for automation or interactive use.
:::

## Checklist

- [ ] **Account scope.** You use an AWS account (or organizational unit) that is appropriate for this workload—often a non-production account or a dedicated sandbox—so billing and blast radius stay predictable.

- [ ] **Billing access.** An owner or finance contact can reach the [AWS Billing and Cost Management console](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/billing-what-is.html). You understand how charges accrue for **S3**, **CloudFront**, and **data transfer** in the Region you choose.

- [ ] **Budgets or alarms (recommended).** You configured at least one [budget](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html) or [CloudWatch billing alarm](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/monitor_estimated_charges_with_cloudwatch.html) so unexpected usage surfaces early.

- [ ] **Root user protection.** The [account root user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-user.html) has **multi-factor authentication (MFA)** enabled. You do **not** use the root user for day-to-day work or for Terraform.

- [ ] **Default Region.** You chose the AWS **Region** where you will create Regional resources (for example S3 buckets). Write it down; Terraform variables and the AWS CLI default should match that choice unless you intentionally operate multi-Region.

- [ ] **Human sign-in.** Operators who need the console can sign in through **IAM Identity Center** (recommended) or **IAM users** with MFA, per your organization’s standard.

- [ ] **Credentials for automation.** You have a supported way to run the AWS CLI and Terraform non-interactively when required: short-lived credentials via **IAM Identity Center** or **IAM role assumption**, or—only if policy allows—[IAM user access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) stored in a secrets manager, **not** in the Git repository.

- [ ] **Permissions for provisioning.** The identity you use for `terraform apply` can create the resource types this project will manage. Until the Terraform module is checked in, treat that as **S3**, **CloudFront**, **IAM** roles and policies, and (if you enable GitHub Actions OIDC from this repo) the **IAM OIDC identity provider** for `token.actions.githubusercontent.com`. Your administrator may need to attach or approve a policy boundary.

- [ ] **CLI sanity check.** From the same environment where you will run Terraform, you can read the caller identity:

    ```bash
    aws sts get-caller-identity
    ```

    The response must show the **account** and **principal** you intend. If the command fails, fix authentication before you continue.

- [ ] **Repository hygiene.** You never commit **access keys**, **session tokens**, **passwords**, `terraform.tfvars` with real values, or Terraform **state** to git. Follow `.gitignore` and the guidance in the repository **`infra/README.md`**.

## What this checklist does not cover

It does not walk through [creating an AWS account](https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-creating.html), organization-level guardrails, or service-specific tutorials. Use [AWS Documentation](https://docs.aws.amazon.com/) for those topics.
