#!/bin/env bash

set -euo pipefail

pytest -vv -x

./scripts/build-documentation.sh
