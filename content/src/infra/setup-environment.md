# Setup: environment

This topic describes how to install and configure the tools you need to create the **Amazon Web Services** assets and deploy the static doc site produced by doc-infra. This requires the following tools:

- Homebrew
- The AWS Command Line Interface (AWS CLI)
- Terraform

::: Note 
It is possible to create the AWS assets manually, without using these tools.
:::

## Homebrew (prerequisite)

::: Note
If you skip Homebrew, install the AWS CLI and Terraform from the official AWS and HashiCorp installers and adapt the verification steps.
:::

These procedures assume **macOS** and that **[Homebrew](https://brew.sh)** is installed. Homebrew is a prerequisite because it gives **one** supported way to install the command-line tools we rely on (for example Terraform and the AWS CLI) with predictable paths and straightforward upgrades. The steps below install each tool **explicitly** in its own subsection; we do not use a single combined install command.

To install Homebrew:

1. Open **Terminal**.
2. Run the install script from the Homebrew project. See [Homebrew](https://brew.sh) for the exact command if the line below does not match your environment. The usual command is:

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

3. Complete the prompts in the installer. On Macs with Apple silicon, the installer prints **Next steps** that add `brew` to your `PATH`. Run those commands in **Terminal** before you continue.
4. Confirm Homebrew works:

   ```bash
   brew --version
   ```

## AWS CLI

To install the **AWS Command Line Interface (AWS CLI)** with Homebrew:

1. Run:

   ```bash
   brew install awscli
   ```

2. Confirm the install:

   ```bash
   aws --version
   ```

See [Installing or updating the latest version of the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) if you need an install path other than Homebrew.

## Terraform

To install **Terraform** with Homebrew:

1. Run:

   ```bash
   brew install terraform
   ```

2. Confirm the install:

   ```bash
   terraform version
   ```

See [Install Terraform](https://developer.hashicorp.com/terraform/install) if you need an install path other than Homebrew.

