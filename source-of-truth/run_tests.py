from pyats.easypy import run

def main():

    # run api launches a testscript as an individual task.
    run('tests/vlan.py')
    run('tests/interface.py')