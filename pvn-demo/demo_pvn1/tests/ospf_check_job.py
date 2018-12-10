# To run the job:
# easypy ospf_check_job.py -testbed_file <testbed_file.yaml>
# Description: This job file
import os
from ats.easypy import run


# All run() must be inside a main function
def main():
    # Find the location of the script in relation to the job file
    ospf_tests = os.path.join('./OSPF_Working.py')
    # Execute the testscript
    # run(testscript=testscript)
    run(testscript=ospf_tests)
