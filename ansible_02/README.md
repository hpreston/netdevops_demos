# Ansible Demo
In this demonstration we'll explore the new `network_cli` connection method as well as multi-platform role creation.  

## "Gitting" the Code
All of the code and examples for this lesson is located in the `netdevops_demos/ansible_02` directory.  Clone and access it with the following commands:

```bash
git clone https://github.com/hpreston/netdevops_demos
cd netdevops_demos/ansible_02
```

## Local Workstation Setup
### Python Environment Setup
It is recommended that this demo be completed using Python 3.6.   

It is highly recommended to leverage Python Virtual Environments for completing exercises in this course.  

Follow these steps to create and activate a venv.  

```bash
# OS X or Linux
virtualenv venv --python=python3.6
source venv/bin/activate
```

***Windows not supported by Ansible***

#### Install Python Requirements for Lesson
With the Virtual Environment activated, use pip to install the necessary requirements.  

```bash
# From the code directory for this lesson
pip install -r requirements.txt
```

## DevNet Sandbox
This lesson leverages the [Open NX-OS with Nexus 9Kv On VIRL](https://devnetsandbox.cisco.com/RM/Diagram/Index/1e9b57ff-9e64-4c68-93e5-f0f0a8c6f22c?diagramType=Topology) Sandbox.  

You will need to reserve an instance of the sandbox, and establish a VPN connection to your individual Sandbox to complete this lab.

### Post Reservation Setup
This lesson leverages a specific [VIRL topology](topology.virl).  Before beginning this lesson run the following command to reconfigure the Sandbox with the proper topology.  

**From the `netdevops_demos/ansible_02` directory**

```bash
# Get a list of currently running simulations
virl ls --all

# Stop any running simulations.
virl down --sim-name API-Test

# Start the VIRL Simulation for demo
virl up

# Monitor status of simulation
virl nodes   # Node startup

# After nodes are "REACHABLE" generage ansible env file
virl generate ansible
```

## Ansible Demo #1
The VIRL simulation starts with a network only cabled and configured with management IPs and administrative credentials.  To push out the initial baseline configuration to the network run the following.  

```bash
ansible-playbook network_deploy.yaml
```

Depending on network and VPN performance, the playbook may fail due to connection timeouts.  Simply re-run the playbook until fully complete.  You can also limit the target of the run to particular network devices with with the following adjustments.  

```bash
# Run against just the "core" routers
ansible-playbook network_deploy.yaml --limit core

# Run against just the "distribution" switches
ansible-playbook network_deploy.yaml --limit distribution

# Run against just the "access" switches
ansible-playbook network_deploy.yaml --limit access
```

## Resetting Demo
You can reset the demo files in this repo by running this command.  

```bash
git reset --hard
```
