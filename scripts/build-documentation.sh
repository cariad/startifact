#!/bin/env bash

set -euo pipefail

rm -rf docs
cd docsrc
make doctest

if [[ "${CI:=}" != "true" ]]; then
  make html
  mv build/html ../docs
  touch ../docs/.nojekyll
fi
