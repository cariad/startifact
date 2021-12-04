"""
**Startifact** is a command line application and Python package for staging and retrieving versioned artefacts in Amazon Web Services.

## Installation

Startifact requires Python 3.8 or later.

Install Startifact via pip:

```bash
pip install startifact
```

## S3 bucket

Startifact will not deploy an S3 bucket for you. You must deploy and own the security yourself.

Startifact requires your bucket's name to be readable from a Systems Manager parameter. This allows you to deploy a bucket without a hard-coded name but still discoverable. [Why do you care what your S3 buckets are named?](https://unbuild.blog/2021/12/why-do-you-care-what-your-s3-buckets-are-named/) explains why Startifact is opinionated.

Here's a complete CloudFormation template you can copy and deploy:

```yaml
Description: Artefact storage
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

## IAM policies

The user performing the one-time organisation setup must be granted:

- `ssm:GetParameter` and `ssm:PutParameter` on the configuration parameter. This is `arn:aws:ssm:{REGION}:{ACCOUNT ID}:parameter/Startifact` by default, but adjust if you are using a different parameter name.

Any users or roles that download artefacts must be granted:

- `ssm:GetParameter` on the configuration parameter.
- `ssm:GetParameter` on the bucket name parameter.
- `ssm:GetParameter` on every parameter beneath the name prefix (or *all* parameters if you have no name prefix).
- `s3:GetObject` on every S3 object in the artefacts bucket beneath the key prefix (or *all* objects if you have no key prefix).

Any users or roles that stage artefacts must be granted:

- `ssm:GetParameter` on the configuration parameter.
- `ssm:GetParameter` on the bucket name parameter.
- `ssm:PutParameter` on every parameter beneath the name prefix (or *all* parameters if you have no name prefix).
- `s3:ListBucket` on the artefacts bucket.
- `s3:PutObject` on every S3 object in the artefacts bucket beneath the key prefix (or *all* objects if you have no key prefix).

## Organisation configuration

Startifact is designed to be run within organisations with multiple CI/CD pipelines that create versioned artefacts.

Rather than configure Startifact within each pipeline, Startifact reads from a shared organisation-level configuration in Systems Manager.

As long as your CI/CD pipelines all authenticate to the same Amazon Web Services account, they will read the same configuration.

### Choosing where to host the configuration

By default, Startifact reads and writes configuration to a Systems Manager parameter named `/Startifact` in your default account and region.

To change that parameter name, set an environment variable named `STARTIFACT_PARAMETER`.

### Performing or updating the organisation setup

Volunteer a privileged human being to run:

```bash
startifact --setup
```

They will be asked to:

1. Confirm the configuration parameter name, region and account.
1. Enter the name of the Systems Manager parameter holding the bucket's name. In the example template above, the parameter is named `/artifacts-bucket`.
1. Enter the name of the region that hosts the Systems Manager parameter that holds the bucket's name.
1. Enter the name of the region that hosts the bucket.
1. Optionally enter a bucket key prefix.
1. Enter the name of the region where artefacts should be recorded in Systems Manager.
1. Optionally enter a name prefix for the Systems Manager parameters that record artefact versions. Without a prefix, versions will be recorded as `/{project}/Latest`.
1. Confirm the configuration parameter name, region and account one last time before committing.

## Command line usage

### Staging an artefact

To stage an artefact, pass the project name, version and `--stage` argument with the path to the artefact:

```text
startifact SugarWater 1.0.9000 --stage dist.tar.gz
```

Where the version number comes from depends on your CI/CD setup. I use Circle CI and I stage artefacts on tags, so I know I can pull the version number from the `CIRCLE_TAG` environment variable:

```text
startifact SugarWater "${CIRCLE_TAG}" --stage dist.tar.gz
```

### Getting the latest version number of a project

To get the version number of the latest artefact staged for a project, pass the project name and `--get` argument for `version`:

```text
startifact SugarWater --get version
```

The version number will be emitted to `stdout`.

### Downloading an artefact

To download an artefact, pass the project name, *optionally* the version number, and the `--download` argument with the path to download to:

```text
startifact SugarWater 1.0.0 --download dist.tar.gz
```

If the version is omitted or `latest` then the latest artefact will be downloaded, otherwise the literal version will be downloaded.

## Project

### Artifact or Artefact?

"Artefact" is the British English spelling. "Artifact" is the American English spelling.

I tend towards American English in code and my native English in documentation.

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

## Python usage
"""

import importlib.resources as pkg_resources
from pathlib import Path

from startifact.session import Session

with pkg_resources.open_text(__package__, "VERSION") as t:
    __version__ = t.readline().strip()
    """
    Startifact package version.
    """


def download(project: str, path: Path, version: str = "latest") -> None:
    """
    Downloads an artefact.
    """

    session = Session()
    session.download(project=project, path=path, version=version)


def get_latest_version(project: str) -> str:
    """
    Gets the latest version of a project.
    """

    session = Session()
    return session.get_latest_version(project)


def stage(project: str, version: str, path: Path) -> None:
    """
    Stages an artefact.

    Raises `startifact.exceptions.ProjectNameError` if the project name is not
    acceptable.

    Raises `startifact.exceptions.AlreadyStagedError` if this version is
    already staged.
    """

    session = Session()
    session.stage(project=project, version=version, path=path)
