rscan
=====

rscan is a python script that makes running relaxed scans with the ab initio software GAMESS automatic.

usage: The current working directory must contain the .inp and .log file of an optimized minimum. Use the following command to begin a relaxed scan

python3 rscan.py min.inp 

Note-The following command must be valid command on your system for submitting a job to GAMESS:
rungms test.inp > test.log


