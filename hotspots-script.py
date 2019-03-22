import subprocess
import csv
from pathlib import Path
import tempfile
import time

init= time.time()

#Get the main branch of the repository
main=input("Type the name of your main branch: ")
branches = []

#Get the git bash response to command
branches_bash=subprocess.check_output("git branch -a", shell=True).decode("UTF-8")
#branches_bash+="remote/origin/WEBVIEW/HTML5/Queen"
remote_branches=branches_bash.strip().split("\n")

#Save the branches in an array. hasNext() doesn't exists in Python iterations so, i had to look the way to find the branches
#with child-branches
for line in remote_branches:

    if "remotes/origin" in line:
        if main not in line:
            split=line.strip().split("/")
            #print(len(split))
            count=2
            for word in split:
                if "remote" not in word:
                    if "origin" not in word:
                        count+=1
                        #print(word)
                        if count < len(split):
                            new_word=word + "/"
                            branches.append(new_word)
                            #print(branches)
                        else:
                            branches.append(word)

#Connect the branches that has been separated by "/"
branches_copy=[]
temp=""
for branch in branches:
    if "/" in branch:
        temp+=branch
    else:
        temp += branch
        branches_copy.append(temp)
        temp=""

#Checkout of every branch existing and coming back to 'main' branch
for branch in branches_copy:
    subprocess.run(["git", "checkout", branch])
subprocess.run(["git", "checkout", main])

#Getting the branches unmerged to main
unm_branches=subprocess.check_output("git branch --no-merged " + main , shell=True).decode("UTF-8")
unm_branches= unm_branches.strip().split()
#print(unm_branches)

#Getting the unmerged commits
commits_bash =""
for unm in unm_branches:
    commits_bash+=subprocess.check_output("git cherry -v " + main +" "+ unm , shell=True).decode("UTF-8")

#Formatting the output because we need the SHA HASH of each commit
lines_of_commits=commits_bash.strip().splitlines()
commits_sha=[]
for cm in lines_of_commits:
    commits_sha.append(cm[2:42])
#print(commits_sha)

#Necessary
date_format="--date=format:%s" % '%Y-%m-%d%H:%M:%S'
pretty_format="--pretty=format:%s" % '%H,%aN,%ad'

#getting the git log of unmerged commits
temporal_file = tempfile.TemporaryFile(mode='w+t', encoding='UTF-8')
try:
    #git_log_unmerged_commits=""
    for cm in commits_sha:
        commit=subprocess.check_output('git log --numstat ' + date_format +' '+ pretty_format + ' -1 ' + cm,shell=True).decode("UTF-8") + "\n"
        temporal_file.writelines(commit)
        temporal_file.seek(0)

    #Getting the git log of merged commits
    temporal_file.writelines(subprocess.check_output('git log --numstat ' + date_format +' '+ pretty_format ,shell=True).decode("UTF-8"))
    temporal_file.seek(0)

    #merging both git logs and separating them by double jump line       
    csv_general_file = Path("../general_commits.csv")
    csv_detailed_file = Path("../detailed_commits.csv")
    with open(csv_general_file, "w", encoding="UTF-8") as output_general_file:
        with open(csv_detailed_file, "w",  encoding="UTF-8") as output_detailed_file:
            writer_general = csv.writer(output_general_file, lineterminator='\n')
            writer_detailed = csv.writer(output_detailed_file,lineterminator='\n')

            header_line_general=["commit_hash","author","date"]
            header_line_detailed=["commit_hash","adds","deletes","files"]

            writer_general.writerow(header_line_general)
            writer_detailed.writerow(header_line_detailed)
            
            line=temporal_file.readline()
            
            while line:
                if "," in line:
                    commit_hash=line.split(",")[0]
                    writer_general.writerow([line])
                    line=temporal_file.readline()

                elif "\t" in line:
                    diff_info=line.strip().split("\t")
                    diff_info.insert(0,commit_hash)
                    writer_detailed.writerow(diff_info)
                    line=temporal_file.readline()

                else:
                    line=temporal_file.readline()             
finally:
    temporal_file.close()

total=time.time() - init
print(total)