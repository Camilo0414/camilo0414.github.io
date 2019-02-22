#!/bin/bash

typeset branches
typeset commits
typeset principal
typeset unm_branches

echo "Type the name of you main branch"
read principal

branches=`git branch -a | nawk -F/ '$1~/remotes/ && $2~/origin/ && $3!~/HEAD/ && $3!~/master/ { print $3} {if($4!="" && $3!~/HEAD/) print "/" $4}'`

for br in $branches ;
do
	git checkout $br 
done
git checkout $principal

unm_branches=`git branch --no-merged $principal` 

echo $unm_branches
#git log --numstat --date=format:'%Y-%m-%d %H:%M:%S' --pretty=format:'%h-%aN-%ad'

#echo $branches
