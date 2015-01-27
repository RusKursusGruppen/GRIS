#!/bin/bash
# -*- coding: utf-8 -*-

time coverage run --omit="env*" tests/tests.py && coverage report
