# NetDevOps CICD Demo 01
This is a basic demo of how network configuration pipelines may look inside of a CICD workflow.  

## Demo Setup

1. Setup Python prerequisites  

```bash
python3.6 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

1. Setup Ansible prerequisites.

```bash
ansible-galaxy install zaxos.docker-ce-ansible-role
```

1. Start "production" network with VIRL

```bash
cd prod_net
virl ls --all

# clear any running simulations

virl up
cd ..
```

1. Setup Pipeline on DevBox

```bash
cd pipeline
ansible-playbook -u root pipeline_setup.yml
cd ..
```

1. Clone down Lab Repo from Gogs

```bash
git clone http://netdevopsuser@10.10.20.20/gogs/netdevopsuser/network_cicd_lab
cd network_cicd_lab
git config user.name "NetDevOps User"
git config user.email "netdevopsuser@netdevops.local"
```

1. Configure the "production network" with starting configuration.

```bash
cd ansible
source ansible_env_prod
ansible-playbook -i hosts_prod playbooks/site.yaml
cd ..
```

1. Start the "Dev" instance in Vagrant

```bash
vagrant up
```

## Demo Run

1. Open the web interfaces for tools

```bash
open http://10.10.20.20/gogs/netdevopsuser/network_cicd_lab -a /Applications/Google\ Chrome.app --args --incognito
open http://10.10.20.20 -a /Applications/Google\ Chrome.app --args --incognito
open http://10.10.20.160:19400/simulations/ -a /Applications/Google\ Chrome.app --args --incognito
open https://web.ciscospark.com -a /Applications/Google\ Chrome.app --args --incognito
open https://cisco.box.com/v/SPT -a /Applications/Google\ Chrome.app --args --incognito
```

1. Exercise 1: Move to “dev” branch in repository

```bash
git fetch
git checkout dev
```

1. Exercise 2: Verify Infrastructure as Code

```bash
# Run against "Dev" instance in Vagrant
cd ansible/
source ansible_env_dev
ansible-playbook -i hosts_dev playbooks/site.yaml
cd ..
```

1. Exercise 3: Activate Repo in Drone

1. Exercise 4: Setup Drone CLI Tool and Secrets

```bash
export DRONE_SERVER=http://10.10.20.20
export DRONE_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZXh0IjoibmV0ZGV2b3BzdXNlciIsInR5cGUiOiJ1c2VyIn0.24hOotRJyhNegtUPRjcyDzK4QyOW3xWWPJeUhozGsYk

# Source Control Credentials
drone secret add --repository netdevopsuser/network_cicd_lab --name GOGS_USER --value netdevopsuser
drone secret add --repository netdevopsuser/network_cicd_lab --name GOGS_PASS --value network

# Spark Credentials for Notifications
# Get token from: https://cisco.box.com/v/SPT
drone secret add --repository netdevopsuser/network_cicd_lab --name SPARK_TOKEN --value <TOKEN VALUE Provided>
drone secret add --repository netdevopsuser/network_cicd_lab --name PERSONEMAIL --value <Your Spark Email>

# VIRL Credentials for Network Simulation Testing
drone secret add --repository netdevopsuser/network_cicd_lab --name VIRL_USER --value guest
drone secret add --repository netdevopsuser/network_cicd_lab --name VIRL_PASSWORD --value guest
drone secret add --repository netdevopsuser/network_cicd_lab --name VIRL_HOST --value http://10.10.20.160:19399
```

1. Exercise 5: Update Pipeline Definition

```.bash
cd ../
open .drone.yml
```

```yaml
# New .drone.yml content
pipeline:
  BuildStart:
    image: hpreston/drone-ansible-netdevops
    commands:
      - echo "Starting Build"
      - git fetch
      - git checkout ${DRONE_BRANCH}

  SparkNotify:
    image: hpreston/drone-spark:0.7
    secrets: [ SPARK_TOKEN, PERSONEMAIL ]
    message: "Build Done!"
    when:
      status: [ success, failure ]
```

1. Exercise 6: Commit changes to Source Control

```bash
git add .drone.yml
git commit -m "Added Notify Phase"
git push
```

1. Exercise 7: Update Pipeline Definition

```yaml
# New .drone.yml content
pipeline:
  BuildStart:
    image: hpreston/drone-ansible-netdevops
    commands:
    - echo "Starting Build"
    - git fetch
    - git checkout ${DRONE_BRANCH}

  Integration-StartTestNetwork:
    image: hpreston/drone-virl:0.7
    virl_file: virl/iosv_test.virl
    simulation_name: Integration_Test
    action: create
    secrets: [ VIRL_USER, VIRL_PASSWORD, VIRL_HOST ]
    when:
      branch: dev

  Integration-ConfigTestNetwork:
    image: hpreston/drone-ansible-netdevops
    commands:
      - cd ansible
      - . ./ansible_env_test
      - ansible-playbook -i hosts_test playbooks/site.yaml
    when:
      branch: dev

  Integration-RunNetworkTests:
    image: hpreston/drone-ansible-netdevops
    commands:
      - cd ansible
      - . ./ansible_env_test
      - ansible-playbook -i hosts_test playbooks/testing-playbook.yml
    when:
      branch: dev

  Integration-DestroyTestNetwork:
    image: hpreston/drone-virl:0.7
    simulation_name: Integration_Test
    action: destroy
    secrets: [ VIRL_USER, VIRL_PASSWORD, VIRL_HOST ]
    when:
      branch: dev

  SparkNotify:
    image: hpreston/drone-spark:0.7
    secrets: [ SPARK_TOKEN, PERSONEMAIL ]
    message: "Build Done!"
    when:
      status: [ success, failure ]
```

1. Exercise 8: Commit changes to Source Control

```bash
git add .drone.yml
git commit -m "Added Integration Phase"
git push
```

1. Exercise 9: Update Pipeline Definition

```yaml
# New .drone.yml content
pipeline:
  BuildStart:
    image: hpreston/drone-ansible-netdevops
    commands:
    - echo "Starting Build"
    - git fetch
    - git checkout ${DRONE_BRANCH}

  Integration-StartTestNetwork:
    image: hpreston/drone-virl:0.7
    virl_file: virl/iosv_test.virl
    simulation_name: Integration_Test
    action: create
    secrets: [ VIRL_USER, VIRL_PASSWORD, VIRL_HOST ]
    when:
      branch: dev

  Integration-ConfigTestNetwork:
    image: hpreston/drone-ansible-netdevops
    commands:
      - cd ansible
      - . ./ansible_env_test
      - ansible-playbook -i hosts_test playbooks/site.yaml
    when:
      branch: dev

  Integration-RunNetworkTests:
    image: hpreston/drone-ansible-netdevops
    commands:
      - cd ansible
      - . ./ansible_env_test
      - ansible-playbook -i hosts_test playbooks/testing-playbook.yml
    when:
      branch: dev

  Integration-DestroyTestNetwork:
    image: hpreston/drone-virl:0.7
    simulation_name: Integration_Test
    action: destroy
    secrets: [ VIRL_USER, VIRL_PASSWORD, VIRL_HOST ]
    when:
      branch: dev

  Delivery-MergeToMaster:
    image: hpreston/drone-ansible-netdevops
    commands:
      - git checkout master
      - git branch -u origin/master
      - git merge dev
      - git push http://$GOGS_USER:$GOGS_PASS@10.10.20.20/gogs/${DRONE_REPO}
    secrets: [ GOGS_USER, GOGS_PASS ]
    when:
      branch: dev

  SparkNotify:
    image: hpreston/drone-spark:0.7
    secrets: [ SPARK_TOKEN, PERSONEMAIL ]
    message: "Build Done!"
    when:
      status: [ success, failure ]
```

1. Exercise 10: Commit changes to Source Control

```bash
git add .drone.yml
git commit -m "Added Delivery Phase"
git push
```

1. Exercise 11: Update Pipeline Definition

```yaml
# New .drone.yml content
pipeline:
  BuildStart:
    image: hpreston/drone-ansible-netdevops
    commands:
      - echo "Starting Build"
      - git fetch
      - git checkout ${DRONE_BRANCH}

  Integration-StartTestNetwork:
    image: hpreston/drone-virl:0.7
    virl_file: virl/iosv_test.virl
    simulation_name: Integration_Test
    action: create
    secrets: [ VIRL_USER, VIRL_PASSWORD, VIRL_HOST ]
    when:
      branch: dev

  Integration-ConfigTestNetwork:
    image: hpreston/drone-ansible-netdevops
    commands:
      - git status
      - cd ansible
      - . ./ansible_env_test
      - ansible-playbook -i hosts_test playbooks/site.yaml
    when:
      branch: dev

  Integration-RunNetworkTests:
    image: hpreston/drone-ansible-netdevops
    commands:
      - git status
      - cd ansible
      - . ./ansible_env_test
      - ansible-playbook -i hosts_test playbooks/testing-playbook.yml
    when:
      branch: dev

  Integration-DestroyTestNetwork:
    image: hpreston/drone-virl:0.7
    simulation_name: Integration_Test
    action: destroy
    secrets: [ VIRL_USER, VIRL_PASSWORD, VIRL_HOST ]
    when:
      branch: dev

  Delivery-MergeToMaster:
    image: hpreston/drone-ansible-netdevops
    commands:
      - git checkout master
      - git branch -u origin/master
      - git merge dev
      - git push http://$GOGS_USER:$GOGS_PASS@10.10.20.20/gogs/${DRONE_REPO}
    secrets: [ GOGS_USER, GOGS_PASS ]
    when:
      branch: dev

  Deployment-ConfigProdNetwork:
    image: hpreston/drone-ansible-netdevops
    commands:
      - cd ansible
      - . ./ansible_env_prod
      - ansible-playbook -i hosts_prod playbooks/site.yaml
    when:
      branch: master

  Deployment-RunNetworkTests:
    image: hpreston/drone-ansible-netdevops
    commands:
      - cd ansible
      - . ./ansible_env_prod
      - ansible-playbook -i hosts_prod playbooks/testing-playbook.yml
    when:
      branch: master

  SparkNotify:
    image: hpreston/drone-spark:0.7
    secrets: [ SPARK_TOKEN, PERSONEMAIL ]
    message: "Build Done!"
    when:
      status: [ success, failure ]
```

1. Exercise 12: Commit changes to Source Control

```bash
git add .drone.yml
git commit -m "Added Deployment Phase"
git push
```

1. Exercise 13: Verify Current SNMP Settings

```bash
# Telnet to a Production Device
telnet 172.16.30.201
```

```
# Verify Current SNMP Community String
sh run | inc community

# *** Expected Output ***
prod-IOSv-1#sh run | inc community
snmp-server community SecureRead RO
snmp-server community SecureWrite RW

# Exit from the production switch
exit
```

1. Exercise 14: Update Ansible Configuration

```bash
# Open Global Variable File for Ansible
open ansible/group_vars/all.yaml
```

```yaml
# Update Read & Write Communities
global_snmp:
  servers:
    - 192.168.100.13
    - 192.168.101.13
  read_community: NewSecureRead    <--
  write_community: NewSecureWrite  <--
  traps_list: snmp linkdown linkup
```

1. Exercise 15: Test Locally Against Vagrant

```bash
cd ansible/
source ansible_env_dev
ansible-playbook -i hosts_dev playbooks/site.yaml
```

1. Exercise 16: Commit changes to Source Control

```bash
git add group_vars/all.yaml
git commit -m "Updated SNMP Community Strings"
git push
```

1. Exercise 17: Verify Current SNMP Settings

```bash
# Telnet to a Production Device
telnet 172.16.30.201
```

```
# Verify Current SNMP Community String
sh run | inc community

# *** Expected Output ***
prod-IOSv-1#sh run | inc community
snmp-server community NewSecureRead RO
snmp-server community NewSecureWrite RW
```

## Demo Cleanup
