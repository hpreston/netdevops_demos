# Configuration Management Demo: Your Network As Code

## "Gitting" the Code
All of the code and examples for this lesson is located in the `netdevops_demos/ansible_01` directory.  Clone and access it with the following commands:

```bash
git clone https://github.com/hpreston/netdevops_demos
cd netdevops_demos/ansible_01
```

## Local Workstation Setup
Be sure to complete the [General Workstation Setup](https://github.com/CiscoDevNet/netprog_basics/blob/master/readme_resources/workstation_setup.md) instructions before beginning this lesson.  

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

**From the `netdevops_demos/ansible_01` directory**

```bash
export VIRL_HOST=10.10.20.160

# Get a list of currently running simulations
virl ls --all

# Stop any running simulations.
virl down --sim-name API-Test

# Start the VIRL Simulation for demo
virl up

# Monitor status of simulation
virl nodes   # Node startup
```

## Ansible Demo #1
The VIRL simulation starts with a network only cabled and configured with management IPs and administrative credentials.  To push out the initial baseline configuration to the network run the following.  

```bash
# Set local environment variables for device credentials
source ansible_env

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

## Ansible Demo #2
Now that the full network is configured, demo how you can easily make network changes with this demo.  

1. Show the current state of the configuration (ie which VLANs and networks are configured).

    ```bash
    # Telnet to Distribution Switch
    telnet 172.16.30.101
    
    # View VLANs and Interfaces
    show vlan brief
    show ip int bri
    
    # disconnect from distribution switch
    exit
    
    # Telnet to Core router
    telnet 172.16.30.111
    
    # Show current routes in OSPF
    show ip route ospf
    
    # disconnect from router
    ```

2. Add a new VLAN to the `group_vars/all.yaml` file.  

    ```bash
    vim group_vars/all.yaml
    ```

    * Add VLAN 201 by updating to match this ([final config](demo_files/all.yaml))

    ```yaml
    vlans:
      - id: 100
        name: Management
        gateway: 172.20.100.1
      - id: 101
        name: Private
        gateway: 172.20.101.1
      - id: 102
        name: Guest
        gateway: 172.20.102.1
      - id: 103
        name: Security
        gateway: 172.20.103.1
      - id: 201
        name: Demo
        gateway: 172.20.201.1
    ```

3. Update the remaining variable files by executing these commands to copy correct and updates to locations.  

    ```bash
    # Copy the rest of the update files
    cp demo_files/all.yaml group_vars/
    cp demo_files/distribution.yaml group_vars/
    cp demo_files/172.16.30.101.yaml host_vars/
    cp demo_files/172.16.30.102.yaml host_vars/
    ```

4. Open and explore the updated files to show what changed.  

5. Run the `demo02.yaml` playbook to apply the changes.  *(You can also re-run the full deployment of (`network_deploy.yaml`), however that takes significantly longer to complete and isn't needed to highlight the specifics of this demo use case.)*  

    ```bash
    ansible-playbook demo02.yaml
    ```

## Resetting Demo
You can reset the demo files in this repo by running this command.  

```bash
git reset --hard
```
