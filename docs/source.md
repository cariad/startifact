---
author: Cariad Eccleston
favicon-emoji: 📦
title: Startifact
---

# 📦 Startifact

**Startifact** is a CLI app and Python package for **st**aging **artifact**s in Amazon Web Services.

## Use Case

Startifact is designed to be used by CI/CD pipelines in which:

- Software projects are continuously versioned, built and staged
- A deployment process continuously discovers and deploys those builds

Startifact contributes on both of these points:

- Startifact helps software projects by providing a CLI app for versioning and staging builds
- Startifact helps deployments by registering artifacts in well-known Systems Manager Parameter Store paths for discovery

## Getting Started

### Prerequisites

Startifact requires **Python 3.8** or later.

### Installation

Install Startifact via `pip`:

```bash
pip install startifact
```

### Initial setup

To ensure Startifact is configured consistently across your suite of projects, it is configured via a Systems Manager Parameter that is read at run-time.

To perform the initial setup, run:

```bash
startifact --setup
```

The operator's IAM policy must grant `ssm:GetParameter` and `ssm:PutParameter` on the configuration parameter. The default parameter name of `/startifact` will have an ARN like `arn:aws:ssm:<REGION>:<ACCOUNT ID>:parameter/startifact`.

## Usage

### Staging an artifact

The first three command line arguments are the **name**, **local path** and **version** of the artifact


```bash
startifact
```
