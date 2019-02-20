#!/bin/bash

git log --branches --not --remotes=*/master --numstat --date=format:'%Y-%m-%d %H:%M:%S'  --pretty=format:'%h-%ad-%aN' > script.log

