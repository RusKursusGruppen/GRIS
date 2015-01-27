#!/bin/bash
# -*- coding: utf-8 -*-

flake8 --max-line-length=80 --exclude="env,gris-old" . | less
