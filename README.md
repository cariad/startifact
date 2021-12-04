# 📦 Startifact

[![codecov](https://codecov.io/gh/cariad/startifact/branch/main/graph/badge.svg?token=DY4aEoo9Th)](https://codecov.io/gh/cariad/startifact)

**Startifact** is a command line application and Python package for staging and retrieving versioned artefacts in Amazon Web Services.

Full documentation is online at [cariad.github.io/startifact](https://cariad.github.io/startifact/startifact.html).

## Installation

```bash
pip install startifact
```

## Configuration

Startifact uses a single shared configuration across all of your CI/CD pipelines.

Full documentation is online at [cariad.github.io/startifact](https://cariad.github.io/startifact/startifact.html).

## Usage

### Staging an artefact

To stage an artefact, pass the project name, version and `--stage` argument with the path to the artefact:

```text
startifact SugarWater 1.0.9000 --stage dist.tar.gz
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

### Licence

Startifact is released at [github.com/cariad/startifact](https://github.com/cariad/startifact) under the MIT Licence.

See [LICENSE](https://github.com/cariad/startifact/blob/main/LICENSE) for more information.

### Author

Hello! 👋 I'm **Cariad Eccleston** and I'm a freelance DevOps and backend engineer. My contact details are available on my personal wiki at [cariad.earth](https://cariad.earth).

Please consider supporting my open source projects by [sponsoring me on GitHub](https://github.com/sponsors/cariad/).
