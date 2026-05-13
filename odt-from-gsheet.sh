#!/usr/bin/env bash
# gsheet->json->odt pipeline

# parameters
DOCUMENT="$1"

# use the project virtualenv when it is available
if [ -x "./venv/bin/python" ]; then
  PYTHON="$(pwd)/venv/bin/python"
else
  PYTHON="python"
fi

# json-from-gsheet
pushd ./gsheet-to-json/src
"${PYTHON}" json-from-gsheet.py --config "../conf/config.yml" --gsheet "${DOCUMENT}"

if [ ${?} -ne 0 ]; then
  popd && exit 1
else
  popd
fi

# odt-from-json
pushd ./json-to-odt/src
"${PYTHON}" odt-from-json.py --config "../conf/config.yml" --json "${DOCUMENT}"

if [ ${?} -ne 0 ]; then
  popd && exit 1
else
  popd
fi
