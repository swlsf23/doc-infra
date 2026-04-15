# Setup: environment

This page describes how to prepare **Amazon Web Services (AWS)**, **Terraform**, **local tooling**, and **GitHub Actions** so you can host the static site produced by doc-infra. We add more detail in a doc-first pass alongside the infrastructure implementation.

## Intended sections

- AWS account and CLI (including single sign-on (SSO))
- Terraform prerequisites and applying the stack
- Deploying the built site from your machine
- Configuring GitHub Actions (OpenID Connect (OIDC), secrets, variables)
