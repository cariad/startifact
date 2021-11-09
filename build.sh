#!/bin/env bash
set -euo pipefail

if [[ -n ${1:-} ]]; then
  version=${1}
elif [[ -n ${CIRCLE_TAG:-} ]]; then
  version=${CIRCLE_TAG}
else
  version="-1.-1.-1"
fi

echo "${version}" > startifact/VERSION

rm -rf docs
mkdir docs
touch docs/.nojekyll

pushd docsrc
rm -rf build
make
popd

rm -rf dist
python setup.py bdist_wheel
rm -rf build
