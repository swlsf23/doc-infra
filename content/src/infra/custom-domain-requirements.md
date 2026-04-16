# Custom domain requirements

This topic lists what you need to serve the static site behind a **hostname you control** (for example **`docs.example.com`**) on **Amazon CloudFront** with **HTTPS**. You do **not** register a new **apex** domain when you already own **`example.com`**. You add a **subdomain** (or use the apex) by combining **DNS**, a **TLS certificate** in **AWS Certificate Manager (ACM)**, and **CloudFront** configuration.

The [Provision AWS hosting](provision-aws-hosting.md) path in this repository starts with the default **`*.cloudfront.net`** URL only. Fulfilling the requirements below is what makes a **custom hostname** end-to-end usable. Step-by-step console clicks stay in **AWS** documentation linked at the end.

::: note
**ACM** certificates used with **CloudFront** must be requested in **AWS Region `us-east-1` (N. Virginia)** even if your **S3** bucket lives elsewhere. That is an **AWS** platform rule, not a choice in this repo.
:::

## Requirements breakdown

1. **Control of DNS for the hostname**  
   You can create or update records for the exact name visitors will use (for example **`docs`** under **`example.com`**). That is usually the same place **`example.com`** is already delegated (**Route 53**, another **DNS** host, or your registrar’s **DNS**).

1. **A public TLS certificate that covers that hostname**  
   Request (or reuse) an **ACM** public certificate whose **subject alternative names** include **`docs.example.com`** or a wildcard such as **`*.example.com`**. Request it in **`us-east-1`**. Private certificates or certificates in other Regions are not valid for **CloudFront**-attached **HTTPS** in the standard pattern.

1. **Proof of control for certificate issuance**  
   Complete **ACM** **DNS validation** (or another validation method **ACM** offers for your case) by publishing the **CNAME** records **ACM** shows you. Issuance cannot finish until validation succeeds.

1. **CloudFront configured for that hostname**  
   The distribution must list the hostname as an **alternate domain name** (sometimes called a **CNAME** in older docs) and must reference the **ACM** certificate in **`us-east-1`** for **HTTPS** between browsers and **CloudFront**. The **S3** origin and **origin access control** behavior stay the same as in the baseline stack.

1. **A public DNS record from the hostname to CloudFront**  
   Create a **DNS** record whose name is **`docs.example.com`** (or your chosen hostname) and whose target is the distribution’s **CloudFront** domain name (for example **`d111111abcdef8.cloudfront.net`**). On **Route 53**, that is usually an **alias** to the distribution. Other **DNS** products typically use a **CNAME** to the same **CloudFront** domain name. Propagation time depends on **TTL** and the provider.

1. **Patience for asynchronous work**  
   **ACM** validation, **CloudFront** configuration updates, and **DNS** propagation each take minutes and sometimes longer. Plan for retries when testing **HTTPS** right after a change.

## Relationship to Terraform in this repository

Today’s **Terraform** root module under `infra/terraform/` provisions the **S3** bucket, **CloudFront** distribution, **OAC**, and bucket policy using the **default CloudFront certificate**. Adding **`docs.example.com`** means extending that module (or a follow-on change set) with at least **alternate domain names**, the **ACM certificate ARN** from **`us-east-1`**, and the right **`viewer_certificate`** block, plus any **Route 53** records you want **Terraform** to own. Until that exists in code, you can still satisfy the requirements above in the **AWS Management Console** and keep **Terraform** focused on the origin stack, as long as you avoid configuration drift you care about.

## AWS documentation links

Use these for detailed procedures and edge cases.

- **ACM** and **CloudFront** (certificate must be in **`us-east-1`**) — [Supported AWS services for use with ACM](https://docs.aws.amazon.com/acm/latest/userguide/acm-services.html)
- **Request a public certificate** — [Requesting a public certificate](https://docs.aws.amazon.com/acm/latest/userguide/gs-acm-request-public.html)
- **DNS validation for ACM** — [DNS validation](https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html)
- **Alternate domain names and HTTPS on CloudFront** — [Using custom URLs](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/CNAMEs.html) and [Using HTTPS with CloudFront](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-https.html)
- **Route 53 alias to a CloudFront distribution** — [Routing traffic to an Amazon CloudFront distribution](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-to-cloudfront-distribution.html)
