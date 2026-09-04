#!/usr/bin/env bash
# Host test runner for the passive_mapper pure-C++ classes.
# Compiles each test with plain g++ (no Arduino/toolchain deps) and runs it.
set -e
cd "$(dirname "$0")"

echo "== DensityWindow =="
g++ -std=c++11 -Wall -Wextra -o /tmp/dw_test tests/test_density_window.cpp
/tmp/dw_test

echo "== SelfCal =="
g++ -std=c++11 -Wall -Wextra -o /tmp/sc_test tests/test_self_cal.cpp -lm
/tmp/sc_test

echo "ALL HOST TESTS PASSED"
