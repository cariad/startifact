#!/bin/env bash
set -euo pipefail

pytest -vv -x

if [[ "${CI:=}" != "true" ]]; then
  pdoc startifact --edit-url startifact=https://github.com/cariad/startifact/blob/main/startifact/ --output-directory docs
fi
