import subprocess
import csv
from pathlib import Path
import re


#Get the main branch of the repository
main=input("Type the name of your main branch: ")
branches = []

#Get the git bash response to command
branches_bash=subprocess.check_output("git branch -a").decode("UTF-8")
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
date_format="--date=format:%s" % '%Y-%m-%d %H:%M:%S'
pretty_format="--pretty=format:%s" % '%H,%aN,%ad'

#getting the git log of unmerged commits
git_log_unmerged_commits=""
for cm in commits_sha:
    git_log_unmerged_commits+=subprocess.check_output(['git', 'log', '--numstat', date_format, pretty_format, "-1", cm],shell=True).decode("UTF-8") + "\n"
#print(git_log_unmerged_commits)

#Getting the git log of merged commits
git_log_merged_commits=subprocess.check_output(['git','log','--numstat',date_format, pretty_format],shell=True).decode("UTF-8")
#print(git_log_merged_commits)

#merging both git logs
git_log_commits = git_log_unmerged_commits + git_log_merged_commits
print(git_log_commits)
git_log_commits= git_log_commits.strip().split("\n\n")
print(git_log_commits)

    


#different outputs depending OS

csvfile = Path("../commits.csv")
csv2_file = Path("../commits2.csv")
with open(csvfile, "w") as output:
    with open(csv2_file, "w") as output_2:
        writer = csv.writer(output, lineterminator='\n')
        writer2= csv.writer(output_2,lineterminator='\n')
        encabezado=["commit_hash","author","date"]
        encabezado2=["commit_hash","adds","deletes","files"]
        writer.writerow(encabezado)
        writer2.writerow(encabezado2)
        for line in git_log_commits:
            line_split=line.split("\n")
            header=line_split[0].split(",")
            writer.writerow(header)
            line_split.pop(0)
            for diff in line_split:
                info_diff = diff.split("\t")
                result = [header[0],info_diff[0],info_diff[1],info_diff[2]]
                writer2.writerow(result)

#with open(csv2_file, "w") as output:
 #   writer = csv.writer(output, lineterminator='\n')
  #  encabezado=["commit_hash","adds","deletes","files"]
   # writer.writerow(encabezado)
    #for line in git_log_commits:
     #   line_split=line.split("\n")
      #  header=line_split[0].split(",")
       # line_split.pop(0)
        #for diff in line_split:
         #   info_diff = diff.split("\t")
          #  result = [header[0],info_diff[0],info_diff[1],info_diff[2]]
           # writer.writerow(result)