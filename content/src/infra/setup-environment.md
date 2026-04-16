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

These procedures assume that **[Homebrew](https://brew.sh)** is installed. Homebrew is a prerequisite because it gives **one** supported way to install the command-line tools we rely on (for example Terraform and the AWS CLI) with predictable paths and straightforward upgrades. Each subsection below installs one tool; we do not use a single combined install command.

To install Homebrew:

1. Open a terminal.

1. Run the install script from the Homebrew project. See [Homebrew](https://brew.sh) for the exact command if the line below does not match your environment. The usual command is:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

1. Complete the prompts in the installer. If the installer prints commands that add `brew` to your `PATH`, run them before you continue.

1. Confirm Homebrew is on your `PATH` and responding:

    ```bash
    brew --version
    ```

## AWS CLI

To install the **AWS Command Line Interface (AWS CLI)** with Homebrew:

1. Run:

    ```bash
    brew install awscli
    ```

1. Confirm the AWS CLI is on your `PATH`:

    ```bash
    aws --version
    ```

See [Installing or updating the latest version of the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) if you need an install path other than Homebrew.

## Terraform

Homebrew installs software from **formula repositories** (collections of build and install definitions). The built-in repository is **homebrew-core**. 

A **tap** is an **additional** formula repository—usually a Git repository on GitHub—that Homebrew registers on your computer when you run `brew tap`. After a tap is added, `brew install` can resolve packages defined in that repository. HashiCorp distributes Terraform through their own tap so releases align with [HashiCorp’s published packages](https://developer.hashicorp.com/terraform/install).

To install **Terraform** with Homebrew:

1. Add the HashiCorp formula repository and install Terraform:

    ```bash
    brew tap hashicorp/tap
    brew install hashicorp/tap/terraform
    ```

    `brew tap hashicorp/tap` registers the repository only. `brew install hashicorp/tap/terraform` downloads and installs the Terraform CLI.

1. Confirm the Terraform CLI is on your `PATH`:

    ```bash
    terraform version
    ```

    Example shape (your version and platform strings will differ):

    ```text
    Terraform v<version>
    on <platform>
    ```

See [Install Terraform](https://developer.hashicorp.com/terraform/install) if you need an install path other than Homebrew.

Before you provision AWS resources in an account, work through the [AWS account checklist](aws-account-checklist.md).
