#!/bin/env bash
set -euo pipefail

pytest -vv

if [[ "${CI:=}" != "true" ]]; then
  edition docs/source.md docs/index.html --press html
  edition docs/source.md README.md       --press markdown
fi
