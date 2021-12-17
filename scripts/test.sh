#!/bin/env bash

set -euo pipefail

pytest -vv

./scripts/build-documentation.sh
