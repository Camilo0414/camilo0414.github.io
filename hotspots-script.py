import subprocess
import csv
from pathlib import Path
import tempfile
from datetime import date, timedelta
import datetime
import time
import sys, getopt
import re
import pandas as pd
import numpy as np

#Get the main branch of the repository by the args and the days to look behind in commits
argv= sys.argv[1:]
main=""
days_to_look=""

try:
    opts, args = getopt.getopt(argv,"b:d:",["main-branch=", "days-behind="])
except getopt.GetoptError:
    print("hotspots-script.py -b <main branch> -d <days to look behind>")
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-b", "--main-branch"):
        main = arg
    elif opt in ("-d", "--days-behind"):
        days_to_look=int(arg)

date_to_look = str(date.today() - timedelta(days=days_to_look))


#Get the git bash response to command
branches = []
branches_bash=subprocess.check_output("git branch -a", shell=True).decode("UTF-8")
remote_branches=branches_bash.strip().split("\n")

#Save the branches in an array. hasNext() doesn't exists in Python iterations so, i had to look the way to find the branches
#with child-branches
for line in remote_branches:

    if "remotes/origin" in line:
        if main not in line:
            split=line.strip().split("/")
            count=2
            for word in split:
                if "remote" not in word:
                    if "origin" not in word:
                        count+=1
                        if count < len(split):
                            new_word=word + "/"
                            branches.append(new_word)
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

#Getting the unmerged commits
commits_bash =""
commits_vs_branch={}
for unm in unm_branches:
    commits_bash+=subprocess.check_output("git cherry -v " + main +" "+ unm , shell=True).decode("UTF-8")
    for cm in commits_bash.strip().splitlines():
        key = cm[2:42]
        commits_vs_branch[key] = unm    

#Formatting the output because we need the SHA HASH of each commit
lines_of_commits=commits_bash.strip().splitlines()
commits_sha=[]
for cm in lines_of_commits:
    commits_sha.append(cm[2:42])

#Necessary
date_format="--date=iso"
#format:%s" % '\'%Y-%m-%d-%H:%M:%S\''
pretty_format="--pretty=format:%s" % '\'%H;%aN;%ad;\''


#getting the git log of unmerged commits
temporal_file = tempfile.TemporaryFile(mode='w+t', encoding='UTF-8')
try:
    commit =""
    for cm in commits_sha:
        commit+=subprocess.check_output('git log --numstat ' + date_format +' '+ pretty_format +' --after=\''+date_to_look+'\''+ ' -1 ' + cm,shell=True).decode("UTF-8")

    #Getting the git log of merged commits
    commit+=subprocess.check_output('git log --numstat ' + date_format +' '+ pretty_format +' --after=\''+date_to_look+'\'',shell=True).decode("UTF-8")
    temporal_file.writelines(commit)
    temporal_file.seek(0)

    #merging both git logs and separating them by double jump line       
    csv_general_file = Path("../general_commits.csv")
    csv_detailed_file = Path("../detailed_commits.csv")
    with open(csv_general_file, "w", encoding="UTF-8") as output_general_file:
        with open(csv_detailed_file, "w",  encoding="UTF-8") as output_detailed_file:
            writer_general = csv.writer(output_general_file, lineterminator='\n', delimiter=';')
            writer_detailed = csv.writer(output_detailed_file,lineterminator='\n', delimiter=';')

            header_line_general=["commit_hash","author","date","branch"]
            header_line_detailed=["commit_hash","adds","deletes","files"]

            writer_general.writerow(header_line_general)
            writer_detailed.writerow(header_line_detailed)
            
            line=temporal_file.readline()                    
            
            while line:
                ismain=True
                if ";" in line:
                    for x, y in commits_vs_branch.items():
                        if x in line:
                            new_line=re.sub("\n", y, line)
                            commit_hash=new_line.split(";")[0]
                            writer_general.writerow([new_line])
                            line=temporal_file.readline()
                            ismain=False
                            break
                else:
                    ismain=False


                if  ismain:
                    new_line=re.sub("\n", main, line)
                    commit_hash=new_line.split(";")[0]
                    writer_general.writerow([new_line])
                    line=temporal_file.readline()

                if "\t" in line:
                    if "\n" in line:
                            new_line=re.sub("\n", "", line)
                            diff_info=new_line.strip().split("\t")
                            diff_info.insert(0,commit_hash)
                            writer_detailed.writerow(diff_info)
                            line=temporal_file.readline()
                else:
                    line=temporal_file.readline()             
finally:
    temporal_file.close()

#the CSV files need one last formatting, so i used pandas to fix it
#general commits csv
df_general_commits = pd.read_csv("../general_commits.csv", sep=";")
data_commit_hashes=df_general_commits['commit_hash']
fixed_commit_hashes=data_commit_hashes.str.replace("'","")
fixed_commit_hashes=fixed_commit_hashes.str.split(pat = ";", expand=True)
fixed_commit_hashes.columns=["commit_hash","author","date","branch"]
final_df_general= pd.DataFrame(fixed_commit_hashes,columns=["commit_hash","author","date","branch"])
export_csv = final_df_general.to_csv(csv_general_file,index=None,header=True)
#detailed commits csv
df_detailed = pd.read_csv("../detailed_commits.csv", sep=";")
df_detailed['commit_hash'] = df_detailed['commit_hash'].apply(lambda x: x.replace("'",""))
export_csv = df_detailed.to_csv(csv_detailed_file,index=None,header=True)