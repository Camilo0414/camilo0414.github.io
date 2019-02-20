#!/bin/bash

git ls-files | xargs wc -l > logs/code_lines.log
