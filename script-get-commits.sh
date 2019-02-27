#!/bin/bash
#remove the log files existing
rm -rf unmerged_commits.log merged_commits.log commits_log lines_file.log

typeset branches
typeset commits
typeset principal
typeset unm_branches

echo "Type the name of you main branch"
read principal

#take all the branches
branches=`git branch -a | nawk -F/ '$1~/remotes/ && $2~/origin/ && $3!~/HEAD/ && $3!~/'$principal'/ { print $0}' | sed 's/remotes\/origin\///'`

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
	git log --numstat --date=format:'%Y-%m-%d %H:%M:%S' --pretty=format:'%H-%aN-%ad' -1 $cm >> unmerged_commits.log
done

#get the log for the merged commits in main branch, in its respectively format
git checkout $principal
git log --numstat --date=format:'%Y-%m-%d %H:%M:%S' --pretty=format:'%H-%aN-%ad' >> merged_commits.log

#mix the commits in the proper format (unmerged - merged)
cat unmerged_commits.log merged_commits.log > commits_log

#get the code lines per file
git checkout $principal
git ls-files | xargs wc -l >> lines_files.log

for bn in $branches ;
do
        git checkout $bn
        git ls-files | xargs c -l >> lines_files.log
done
git checkout $principal
#¿los archivos deberían ser únicos? archivos transversales al proyecto que se modifiquen en distintos puntos
cat lines_files.log | sort | uniq | xargs wc -l > code_lines_file.log
#nawk para sumar y totalizar
total_lines=`cat code_lines_file.log | nawk '$2~/total/ {print $1}'`

while read -r line;
do
	amount=$((amount+$line))
done <<< "$total_lines"
cat code_lines_file.log | sed '/total/d' > code_lines.log && echo " $amount total" >> code_lines.log
