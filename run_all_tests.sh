#!/bin/bash

base_dir=$(cd $(dirname $0) && pwd)
export PYTHONPATH="$PYTHONPATH:${base_dir}"
export TEST_INFO="${base_dir}/test-info.yml.example"
export TORTURE_TESTS="${base_dir}/testcases/smbtorture-test/smbtorture-tests-info.yml"
pytest -v tests
