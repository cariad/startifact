---
author: Cariad Eccleston
favicon-emoji: 📦
title: Startifact
---

# 📦 Startifact

**Startifact** is a CLI app and Python package for staging, versioning and downloading artifacts from Amazon Web Services.

Startifact uses a shared configuration held in Systems Manager so all of your CI/CD jobs automatically pick up the same configuration.

<edition value="toc" hi="2" />

## Getting Started

### Prerequisites

- Python 3.8 or later.
- [S3 bucket with the name recorded in Systems Manager](#deploying-an-s3-bucket).

### Installation

Install Startifact via pip:

```bash
pip install startifact
```

## Deploying an S3 bucket

It's essential to note that Startifact will not let you configure the name of your S3 artifacts bucket directly. You must set the name of a Systems Manager parameter where the bucket's name can be read.

_Why?_

The short answer is: so you don't have to deploy buckets with hard-coded names. But why is that a bad thing?

Remember that bucket names are globally unique. If your organisation is in the habit of naming buckets with a well-known schema, like "org.development.frontend" and "org.production.assets", it wouldn't take a malicious actor long to realise that they can squat on the bucket, say, "org.development.new-feature" and ruin your automation. **Patterns are exploitable.**

I choose to be pessimistic about the bucket names available to me. When I deploy buckets via CloudFormation, I omit their names and let CloudFormation pick any available name for me. In that same template, I also create a Systems Manager parameter that holds the bucket's generated name for later reference.

Here's a complete CloudFormation template you can copy, paste and deploy:

```yaml
Description: Artifact storage
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  BucketParameter:
    Type: AWS::SSM::Parameter
    Properties:
      # This name can be anything you want:
      Name: /artifacts-bucket
      Type: String
      Value:
        Ref: Bucket
```

## Organisation setup

### Introduction

Startifact is designed to be used within organisations with multiple CI/CD jobs that push and pull artifacts.

Startifact achieves this with a single shared configuration, rather than needing every CI/CD job to be individually configured to match the others.

Startifact uses Systems Manager Parameter Store to host the single shared configuration.

### Choosing where to host the configuration

By default, Startifact reads and writes configuration to a Systems Manager parameter named `/startifact` in your default account and region.

To change that parameter name, set an environment variable named `STARTIFACT_PARAMETER`.

### Performing or updating the organisation setup

```bash
startifact --setup
```

### Questions

#### Q1: Confirm the configuration parameter location

You will be asked to confirm the name and location of the shared configuration parameter.

To change the name of the parameter, stop the setup then set an environment variable named `STARTIFACT_PARAMETER`.

To change the account or region, stop the setup then adjust your Amazon Web Services credentials.

#### Q2: Bucket name parameter

You will be asked to enter the name of the Systems Manager parameter that holds the name of your artifacts bucket.

See [Deploying an S3 bucket](#deploying-an-s3-bucket) for more information.

If you copied and deployed the example CloudFormation template exactly then your bucket parameter is named "/artifacts-bucket".

#### Q3: Bucket name parameter region

You will be asked to enter the region that holds the bucket name parameter you entered in Question 2.

This can be different from the region where the bucket itself is deployed.

#### Q4: Bucket region

You will be asked to enter the region that holds the artifacts bucket itself.

This can be different from the region where the bucket's name parameter is deployed.

#### Q5: Bucket key prefix

You will be asked to enter any key prefix you want Startifact to use in the artifacts bucket.

The prefix is optional and will be empty by default.

#### Q6: Artifact parameter region

The latest staged version of each artifact will be recorded in System Manager parameters. These parameters can be created in any region.

#### Q7: Artifact parameter name prefix

By default, the latest staged version of each artifact will be recorded in a Systems Manager parameter named "/NAME/latest".

If you specify the name prefix "/org-" then parameters will be named "/org-NAME/latest".

If you specify the name prefix "/org/" then parameters will be named "/org/NAME/latest".

#### Q8: Confirmation

This is your last chance to verify the configuration before it is saved.

When saved, changes take effect immediately across your entire organisation.

## IAM policies

The user performing the organisation setup must be granted:

- `ssm:GetParameter` and `ssm:PutParameter` on the configuration parameter. This is `arn:aws:ssm:{REGION}:{ACCOUNT ID}:parameter/startifact` by default, but adjust if you are using a different parameter name.

Any users or roles that download artifacts must be granted:

- `ssm:GetParameter` on the configuration parameter.
- `ssm:GetParameter` on every parameter beneath the name prefix (or _all_ parameters if you have no name prefix).
- `s3:GetObject` on every S3 object in the artifacts bucket beneath the key prefix (or _all_ objects if you have no key prefix).

Any users or roles that stage artifacts must be granted:

- `ssm:GetParameter` on the configuration parameter.
- `ssm:PutParameter` on every parameter beneath the name prefix (or _all_ parameters if you have no name prefix).
- `s3:ListBucket` on the artifacts bucket.
- `s3:PutObject` on every S3 object in the artifacts bucket beneath the key prefix (or _all_ objects if you have no key prefix).

## Usage

### CLI usage

#### Staging an artifact via the CLI

```text
startifact my-project 1.0.0 --stage README.md
```

#### Getting the latest version number of a project via the CLI

The version number will be emitted to `stdout`.

```text
startifact my-project --get version
```

#### Downloading the latest version of an artifact via the CLI

```text
startifact my-project --download ./my-project-latest.tar.gz
```

#### Downloading a specific version of an artifact via the CLI

```text
startifact my-project 1.0.1 --download ./my-project-1.0.1.tar.gz
```

### Python usage

#### Staging an artifact via Python

```python
from startifact import stage

stage("my-project", "1.0.0", "./dist.tar.gz")
```

#### Getting the latest version number of a project via Python

```python
from startifact import get_latest_version

version = get_latest_version("my-project")
```

#### Downloading the latest version of an artifact via Python

```python
from startifact import download

download("my-project", "./my-project.tar.gz")
```

#### Downloading a specific version of an artifact via Python

```python
from startifact import download

download("my-project", "./my-project.tar.gz", version="1.0.0")
```


## Project

### Contributing

To contribute a bug report, enhancement or feature request, please raise an issue at [github.com/cariad/startifact/issues](https://github.com/cariad/startifact/issues).

If you want to contribute a code change, please raise an issue first so we can chat about the direction you want to take.

### Licence

Startifact is released at [github.com/cariad/startifact](https://github.com/cariad/startifact) under the MIT Licence.

See [LICENSE](https://github.com/cariad/startifact/blob/main/LICENSE) for more information.

### Author

Hello! 👋 I'm **Cariad Eccleston** and I'm a freelance DevOps and backend engineer. My contact details are available on my personal wiki at [cariad.earth](https://cariad.earth).

Please consider supporting my open source projects by [sponsoring me on GitHub](https://github.com/sponsors/cariad/).

### Acknowledgements

- Interactive configuration by [Asking](https://github.com/cariad/asking).
- CLI orchestration by [Cline](https://github.com/cariad/cline).
- Command line colours and styling by [Ansiscape](https://github.com/cariad/ansiscape).
- This documentation was pressed by [Edition](https://github.com/cariad/edition).
