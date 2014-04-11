# Branching
When you fix something on GRIS, then create an issue on github
(iss42, where 42 is the number of the issue). Then assign yourself to the issue.

Then make a branch to work on the issue.
Use the following commands:
```
git checkout -b iss42
git push -u origin iss42
```
Do some work.
When your work is done, then commit and push your work.
Then merge your branch with the master and delete the branch.
Use the following commands:
```
git checkout master
git merge iss42
git branch -d iss42
git push origin --delete iss42
...
