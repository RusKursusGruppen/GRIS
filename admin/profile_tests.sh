#!/bin/bash
# -*- coding: utf-8 -*-

python -m cProfile -s tottime tests/tests.py > profile-test-results.txt
less profile-test-results.txt
