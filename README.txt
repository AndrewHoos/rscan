rscan
=====

rscan is a python script that makes running relaxed scans with the ab initio software GAMESS automatic.

usage: The current working directory must contain the .inp and .log file of an optimized minimum. call

python3 rscan.py input.inp > input.log

Note-The following command must be valid command for submitting a job to GAMESS:
rungms test.inp > test.log


