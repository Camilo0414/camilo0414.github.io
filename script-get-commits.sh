#!/bin/bash

typeset branches
typeset commits
typeset principal
typeset unm_branches

echo "Type the name of you main branch"
read principal

#take all the branches
branches=`git branch -a | nawk -F/ '$1~/remotes/ && $2~/origin/ && $3!~/HEAD/ && $3!~/master/ { print $3} {if($4!="" && $3!~/HEAD/) print "/" $4}'`

#load in the local the branch stuff
for br in $branches ;
do
	git checkout $br 
done

git checkout $principal
unm_branches=`git branch --no-merged $principal` 

#get the commits that hasn't been merged
for unm in $unm_branches ;
do
	commits=`git cherry -v $principal $unm | nawk '{print $2}'`
	#git log --numstat --date=format:'%Y-%m-%d %H:%M:%S' --pretty=format:'%h-%aN-%ad'
done

#get the log for the unmerged commits, in its respectively format, and save it in the log directory
for cm in $commits ;
do
	git log --numstat --date=format:'%Y-%m-%d %H:%M:%S' --pretty=format:'%h-%aN-%ad' -1 $cm >> unmerged_commits.log
done

#get the log for the merged commits in main branch, in its respectively format
git checkout $principal
git log --numstat --date=format:'%Y-%m-%d %H:%M:%S' --pretty=format:'%h-%aN-%ad' >> merged_commits.log

#mix the commits in the proper format (unmerged - merged)
cat unmerged_commits.log merged_commits.log > commits_log

#get the code lines per file
git checkout $principal
git ls-files | xargs wc -l >> lines_file.log
cat lines_file.log | uniq > code_lines_file.log


