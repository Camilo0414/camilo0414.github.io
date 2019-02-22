#!/bin/bash

typeset branches
typeset after
typeset before
typeset commits

branches=`git branch -a | nawk -F/ '$1~/remotes/ && $2~/origin/ && $3!~/HEAD/ && $3!~/master/ { print $3} {if($4!="" && $3!~/HEAD/) print "/" $4}'`

echo -e "Please, type the date since when you want your commit history. /nFormat YYYY-MM-DD HH:MM:SS/n"
read after
echo -e "Please, type the date until when you want your commit history. /nFormat YYYY-MM-DD HH:MM:SS/n"
read before

for br in $branches;
do
#	git checkout $b | git log --branches
#commits=``
echo $branches
