# NetDevOps Tools from Cisco Demo
NetDevOps is becoming a networking phenomenon the likes of which hasn’t been seen since Auto MDI-X or POE. NetDevOps Engineers everywhere are reading the DevOps Handbook, signing up for GitHub accounts, and covering their laptops in stickers.  In this demonstration you will learn about **three tools from Cisco** that you can begin to use **TODAY** in your NetDevOps Journey.  

There is no better network configuration management tool than [**Cisco NSO**](https://developer.cisco.com/nso).  It will immediately provide you a *single CLI, API and GUI* for your entire existing network. It’s *multi-vendor*, supporting 100s of devices across. It let’s you model and simulate existing network configurations right on your laptop.  And now, it’s [***FREELY available on Cisco DevNet***](https://developer.cisco.com/docs/nso/#!getting-nso).  

When the time comes to test your network configurations BEFORE heading off to production, look no further than [**Cisco VIRL and it’s big brother CML**](https://virl.cisco.com).  These robust tools allow engineers to *build virtual representations of their network* that offer feature parity with physical devices. And like NSO, *VIRL is multi-vendor* and device allowing you to import and use your own templates. And with [`virlutils`](https://github.com/CiscoDevNet/virlutils), NetDevOps engineers now have a command line interface for managing their simuluations.  

But how do you test and validate the network?  That’s where [**pyATS and Genie** ](https://developer.cisco.com/pyats)come in.  Launched at the beginning of 2018 and made available for *FREE on DevNet*, pyATS is a Python test framework for profiling and validating networks are operating as designed. Is OSPF healthy?  Are your trunks trunking?  Are you dropping packets where you shouldn’t?  pyATS let’s you find out what’s wrong before the phone rings.  

## Table of Contents

* [Demo Preparation](#demo-preparation)
* [Part 1: NSO](#part-1-nso)
    * [NSO Getting Started](#nso-getting-started)
    * [NSO Demo - Experimenting Locally with netsim and NSO](#nso-demo---experimenting-locally-with-netsim-and-nso)
    * [NSO Demo - Including NSO with NetSim](#nso-demo---including-nso-with-netsim)
    * [NSO Demo - Preventing Cowboy Engineering](#nso-demo---preventing-cowboy-engineering)
    * [Demo Clean up](#demo-clean-up)
* [Part 2: Let's get some "real" devices with VIRL](#part-2-lets-get-some-real-devices-with-virl)
    * [VIRL Demo: Starting up a Network](#virl-demo-starting-up-a-network)
    * [Demo: Setup a new NSO instance and connect with the VIRL topology](#demo-setup-a-new-nso-instance-and-connect-with-the-virl-topology)
    * [Demo: Managing Configuration with Groups and Policies](#demo-managing-configuration-with-groups-and-policies)
* [Part 3: But is the net-working? Bring on pyATS and Genie!](#part-3-but-is-the-net-working--bring-on-pyats-and-genie)
    * [Demo: Generate a pyATS testbed from VIRL](#demo-generate-a-pyats-testbed-from-virl)
    * [Demo: Testing if OSPF is working](#demo-testing-if-ospf-is-working)
* [Demo Cleanup](#demo-cleanup)

## Demo Preparation

### Demonstration Infrastructure Used
To run this demonstration you'll need:

* Either a macOS or Linux development workstation
    * Python 3.6 (newer and older versions of Python may work, but the demo was built and tested with 3.6)
* A Cisco VIRL (or CML) instance

If you'd like, you can leverage a [DevNet Sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/1e9b57ff-9e64-4c68-93e5-f0f0a8c6f22c?diagramType=Topology). This sandbox includes a CentOS 7 devbox and a Cisco VIRL server where you can run the entire lab from.

### Preparing your Environment

1. Clone down the code directory, and change to demo directory.

    ```bash
    git clone https://github.com/hpreston/netdevops_demos
    cd netdevops_demos
    ```

1. Create a Python3.6 Virtual Environment

    ```bash
    python3.6 -m venv venv
    source venv/bin/activate
    ```

1. Install the Python libraries needed.

    ```bash
    pip install virlutils pyats genie ipython
    ```

1. "Source" the `env_demo` file to set NSO and pyATS environment variables for hosts, usernames, and passwords.  

    ```bash
    source env_demo
    ```

# Part 1: NSO
In this first round of demo's, we'll get started with Cisco NSO completely locally, starting by downloading and installing it on our workstation.  

## NSO Getting Started

1. Download Cisco NSO from [DevNet](https://developer.cisco.com/docs/nso/#!getting-nso).

1. Unzip and install NSO. *Adjust the commands for the version (darwin/linux) you are using.*

    ```bash
    # Change into the download directory
    unzip nso-4.7.darwin.x86_64.zip
    cd nso-4.7.darwin.x86_64
    sh nso-4.7.darwin.x86_64.signed.bin
    sh nso-4.7.darwin.x86_64.installer.bin $HOME/ncs47 --local-install
    ```

1. "Source" the `ncsrc` file to use NSO.

    ```bash
    source $HOME/ncs47/ncsrc
    ```

1. Open the Docs

    ```bash
    open $HOME/ncs47/doc/index.html
    ```

1. Look at the included device neds (packages).

    ```bash
    ls -l $HOME/ncs47/packages/neds/
    ```

## NSO Demo - Experimenting Locally with netsim and NSO

1. Change into the `demo_nso1` directory.

    ```bash
    cd demo_nso1
    ```

1. Look at the netsim command options.  

    ```bash
    ncs-netsim --help
    ```

1. Create a new network of 4 NX-OS devices.

    ```bash
    ncs-netsim create-network cisco-nx 4 nxos
    ```

1. Add some IOS devices to the network.

    ```bash
    ncs-netsim add-to-network cisco-ios 4 ios
    ```

1. Add some Junos devices.  

    ```bash
    ncs-netsim add-to-network juniper-junos 2 junos
    ```

1. Start the network.  

    ```bash
    ncs-netsim start
    ```

1. Connect to the devices with CLI.  Run some commands to see what's there.  

    ```bash
    ncs-netsim cli-c nxos0

    show running-config interface
    show running-config vlan
    exit

    ncs-netsim cli-c ios0

    show running-config router bgp
    exit

    ncs-netsim cli-c junos0

    show running-config
    exit

    ncs-netsim cli junos0

    show configuration
    exit

    ncs-netsim cli ios

    show configuration
    exit
    ```

1. We can also add configuration with CLI.  

    ```bash
    ncs-netsim cli-c ios0

    config t
    interface GigabitEthernet 3/1
      description Configured with NetSim CLI
      no switchport
      ip address 10.10.10.1 255.255.255.0
      no shut
      exit

    commit
    exit
    ```

## NSO Demo - Including NSO with NetSim

1. Still in the `demo_nso1` directory.

1. Setup a NSO instance.  

    ```bash
    ncs-setup --dest ./nso --package cisco-ios --package cisco-nx --package juniper-junos
    ```

1. Start NSO

    ```bash
    cd nso
    ncs
    cd ..
    ```

1. Log into NSO command line.

    ```bash
    ncs_cli -C -u admin
    ```

1. Verify the netsim devices were included, and "sync-from" to pull configurations into NSO.  

    ```bash
    show devices list
    devices sync-from
    ```

1. Explore the device configurations from NSO

    ```bash
    show running-config devices device ios0 config
    show running-config devices device ios0 config ios:interface

    show running-config devices device junos0 config
    show running-config devices device junos0 config junos:configuration interfaces

    show running-config devices device nxos0 config
    show running-config devices device nxos0 config nx:interface
    ```

1. Update configuration from NSO

    ```bash
    config t
    devices device ios0
    config
    ios:interface GigabitEthernet 3/2
    description Configured with NSO CLI
    no switchport
    ip address 10.10.20.1 255.255.255.0
    no shut
    exit
    ```

1. In another tab, connect to the CLI for ios0. See that new interface isn't created yet.  

    ```bash
    ncs-netsim cli-c ios0

    show running-config interface
    ```

1. Back on NSO, commit the change.  

    ```bash
    commit
    ```

1. And verify the interface is now on ios0

    ```bash
    show running-config interface
    ```

## NSO Demo - Preventing Cowboy Engineering

1. Connect to ios0 CLI directly, and add a new interface (your a cowboy)

    ```bash
    ncs-netsim cli-c ios0

    config t
    interface GigabitEthernet 3/3
      description CowBoy Interface
      no switchport
      ip address 10.10.30.1 255.255.255.0
      no shut
      exit
      commit
      end

    show running-config interface GigabitEthernet 3/3
    ```

1. Return to NSO and check what's going on.  

    ```bash
    show running-config devices device ios0 config ios:interface

    devices check-sync

    devices device ios0 compare-config
    ```

1. You've options now... you can "sync-to" to "undo" the cowboy, or "sync-from" to accept the local change.  

    ```bash
    devices device ios0 sync-to
    ```

1. Go back to the ios0 device, and see it has been returned.  

    ```bash
    show running-config interface GigabitEthernet 3/3

    show running-config interface
    ```

## Demo Clean up

1. Exit out of CLI for any devices and NSO.  

1. Stop NSO and netsim

    ```bash
    ncs --stop
    ncs-netsim stop
    ```

1. From the demo_nso1 directory, delete the `netsim` and `nso` folders.  

    ```bash
    rm -Rf netsim nso
    ```

1. Move back to demo root directory (`pvn-demo`).

    ```bash
    cd ..
    ```

# Part 2: Let's get some "real" devices with VIRL
You can do a lot with netsim devices, but eventually you'll likely want to work on something that can actually pass traffic and setup protocols. While having "real physical" devices would be great, it can also be difficult, expensive, and a hassle to maintain a physical lab.  

Cisco VIRL/CML and the open source `virlutils` command line, provide engineers "Simulation as Code" opportunities for their NetDevOps explorations.  

## VIRL Demo: Starting up a Network

1. Change into the `demo_pvn1` directory.  

    ```bash
    cd demo_pvn1
    ```

1. First let's see if anything is running in VIRL.  Stop anything we don't want.

    ```bash
    virl ls --all
    virl down --sim-name {SIM-NAME}
    ```

1. See find a sample topology to start up.  

    ```bash
    virl search
    virl up virlfiles/5_router_mesh
    virl nodes
    ```

1. Checkout the status in the web interface.  

    ```bash
    virl uwm
    ```

1. Monitor startup with console.  When avialable, telnet.  

    ```bash
    virl console iosv-1
    virl telnet iosv-1
    ```

1. Take a look at the `topology.virl` file.  This is "Simulation as Code" and describes the network, connections, and initial configuration.  

## Demo: Setup a new NSO instance and connect with the VIRL topology

1. Run ncs-setup, but only need cisco-ios this time.  Also start ncs.

    ```bash
    ncs-setup --package cisco-ios --dest ./nso
    cd nso
    ncs
    cd ..
    ```

1. Log into NSO, check what devices exist.  

    ```bash
    ncs_cli -C -u admin
    show devices list
    exit
    ```

1. Generate an NSO inventory from VIRL.

    ```bash
    virl generate nso
    ```

1. Check NSO again.  "sync-from" the network.  

    ```bash
    show devices list
    devices sync-from
    ```

1. Show that the configuration is in NSO now.  

    ```bash
    show running-config devices device iosv-1 config ios:interface
    ```

## Demo: Managing Configuration with Groups and Policies

1. Let's create a new device group for our routers.  

    ```bash
    config
    devices device-group ios-routers
    device-name [ iosv-1 iosv-2 iosv-3 iosv-4 iosv-5 ]
    commit
    end
    show devices device-group ios-routers member
    ```

1. Use the device-group to check status.  

    ```bash
    devices device-group ios-routers check-sync
    ```

1. Let's create a configuration template to enable OSPF routing.  

    ```bash
    config
    devices template OSPF_Enabled
    config
    ios:router ospf 1
    non-vrf network 10.0.0.0 0.0.0.255 area 0
    commit
    end
    ```

1. Now apply the template to the group

    ```bash
    config
    devices device-group ios-routers apply-template template-name OSPF_Enabled
    ```

1. Check a device configuration in NSO.  

    ```bash
    show configuration devices device iosv-1 config ios:router
    ```

1. Log into one of the network devices and check OSPF configuration.  

    ```bash
    virl telnet iosv-1
    show run | section router
    ```

1. Commit the change in NSO.  

    ```bash
    commit
    ```

1. Log into one of the network devices and check OSPF configuration.  

    ```bash
    virl telnet iosv-1
    show run | section router
    show ip route ospf
    ```

1. Let's build a compliance report to verify that configuration matches template.

    ```bash
    config
    compliance reports report OSPF_Enabled
    compare-template OSPF_Enabled ios-routers
    commit
    end
    ```

1. Run the compliance report.  

    ```bash
    compliance reports report OSPF_Enabled run outformat html
    ```

1. Import a policy and report from an external file.  

    ```bash
    config
    load merge policies/DNS_Server_Policy.xml
    commit
    end
    ```

1. Run the compliance report for new template.  

    ```bash
    compliance reports report DNS_Servers_Configured run outformat html
    ```

1. Apply the new template

    ```bash
    config
    devices device-group ios-routers apply-template template-name Standard_DNS_Servers
    commit
    ```

1. Run the compliance report for new template.  

    ```bash
    compliance reports report DNS_Servers_Configured run outformat html
    ```

# Part 3: But is the net-working?  Bring on pyATS and Genie!
Managing network configuration with ease is great, but is the network actually healthy? Are those configurations operating as expected? Now we'll see how you can answer those questions with confidence using pyATS and Genie.  

## Demo: Generate a pyATS testbed from VIRL

1. Still in the `demo_pvn1` directory.

1. Use virlutils to automatically create a pyATS testbed file.  

    ```bash
    virl generate pyats
    ```

1. Open `default_testbed.yaml` and review.  

1. Update testbed file for "iosxe".  

## Demo: Testing if OSPF is working

1. Source the env_demo file.

1. Kickoff the test.

    ```bash
    cd tests
    easypy ospf_check_job.py -html_logs . -testbed_file ../default_testbed.yaml
    ```

1. In another terminal, let's dig in a bit to what pyATS and Genie do.

1. Source the env_demo file.

1. Start an iPython session

    ```python
    # Import pyATS and Genie objects
    from ats.topology import loader # Load a Testbed file
    from genie.conf import Genie # Load Genie base object
    from genie.abstract import Lookup # Ability to Lookup details about a device
    from genie.libs import ops # "show run" stuff

    # Read in the testbed file for pyATS and Genie
    testbed = 'default_testbed.yaml'
    testbed = loader.load(testbed)
    testbed = Genie.init(testbed)

    # Connect to one of the routers
    iosv2 = testbed.devices['iosv-2']
    iosv2.connect()

    # Allow Genie to inspect device to determine what commands/parsers to use
    abstract = Lookup.from_device(iosv2)

    # Learn all about interfaces on device
    interfaces = abstract.ops.interface.interface.Interface(iosv2)
    interfaces.learn()

    # Checkout what was learned
    interfaces.info["GigabitEthernet0/1"]
    interfaces.info["GigabitEthernet0/1"]["counters"]

    # Learn about OSPF
    ospf = abstract.ops.ospf.ospf.Ospf(iosv2)
    ospf.learn()

    # See what was learned
    ospf.info

    # Make some convenient variables
    default_vrf = ospf.info["vrf"]["default"]
    ipv4 = default_vrf["address_family"]["ipv4"]
    instance = ipv4["instance"]["1"]
    area0 = instance["areas"]["0.0.0.0"]

    # Explore details
    area0["interfaces"]["GigabitEthernet0/2"]
    area0["database"]["lsa_types"][1]["lsas"]["192.168.0.5 192.168.0.5"]
    area0["database"]["lsa_types"][2]["lsas"]["10.0.0.42 192.168.0.5"]
    ```

1. Now go check on the status of the tests. Look at the final results, as well as scroll to tables and details.  

1. Open the HTML report.  

    ```bash
    open TaskLog.html
    ```

# Demo Cleanup

1. Shutdown NSO and delete NSO instance.

    ```bash
    ncs --stop
    rm -Rf nso/
    ```

1. Shutdown VIRL simulation

    ```bash
    virl down
    ```
