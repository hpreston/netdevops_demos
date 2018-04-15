# Application Centric Infrastructure and Ansible

## "Gitting" the Code
All of the code and examples for this lesson is located in the `netdevops_demos/ansible_aci01` directory.  Clone and access it with the following commands:

```bash
git clone https://github.com/hpreston/netdevops_demos
cd netdevops_demos/ansible_aci01
```

## Local Workstation Setup
<!-- Be sure to complete the [General Workstation Setup](https://github.com/CiscoDevNet/netprog_basics/blob/master/readme_resources/workstation_setup.md) instructions before beginning this lesson.   -->

### Python Environment Setup
It is recommended that this lesson be completed using Python 3.6.   

It is highly recommended to leverage Python Virtual Environments.

Follow these steps to create and activate a venv.  

```bash
# OS X or Linux
python3.6 -m venv venv
source venv/bin/activate
```

```bash
py -3 -m venv venv
venv/Scripts/activate
```

#### Install Python Requirements for Lesson
With the Virtual Environment activated, use pip to install the necessary requirements.  

```bash
# From the code directory for this lesson
pip install -r requirements.txt
```

## DevNet Sandbox
This lesson leverages the [Always On: ACI APIC](https://devnetsandbox.cisco.com/RM/Diagram/Index/5a229a7c-95d5-4cfd-a651-5ee9bc1b30e2?diagramType=Topology) Sandbox.  This sandbox requires no reservation **or** VPN connection.  
