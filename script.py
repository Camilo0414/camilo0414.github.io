import subprocess
import csv


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

unm_branches=subprocess.check_output("git branch --no-merged " + main , shell=True).decode("UTF-8")
unm_branches= unm_branches.strip().split()
#print(unm_branches)

commits_bash =""
for unm in unm_branches:
    commits_bash+=subprocess.check_output("git cherry -v " + main +" "+ unm , shell=True).decode("UTF-8")

lines_of_commits=commits_bash.strip().splitlines()
commits_sha=[]
for cm in lines_of_commits:
    commits_sha.append(cm[2:42])
#print(commits_sha)

#Necessary
date_format="%Y-%m-%d %H:%M:%S"
pretty_format="%H-%"+"aN-%"+"ad"
#--numstat --date=format:'"+date_format+"' --pretty=format:'"+pretty_format+"'

##FORMAT TROUBLE

git_log_unmerged_commits=""
for cm in commits_sha:
    git_log_unmerged_commits+=subprocess.check_output("git log --numstat -1 " + cm,shell=True).decode("UTF-8")
#print(git_log_unmerged_commits)

git_log_merged_commits=subprocess.check_output("git log --numstat",shell=True).decode("UTF-8")
#print(git_log_merged_commits)

git_log_commits = git_log_unmerged_commits + git_log_merged_commits

print(git_log_commits)


csvfile="C:\\Users\\jibanezn\\Documents\\file.csv"

#Assuming res is a flat list
with open(csvfile, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    for val in git_log_commits.strip().split("\n"):
        writer.writerow([val]) 

#print(branches_copy)
#print(branches)

#get subprocess
#output=subprocess.check_output("git status", shell=True)
#decode UTF-8
#output_decoded=output.decode("UTF-8")
#print(output_decoded)
