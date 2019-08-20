# Source of Truth Demonstrations 
The demo's included here are meant to show how a Source of Truth factors into network automation workflows.  For these demonstrations the open source tool [Netbox](https://netbox.readthedocs.io) is being used as the source of truth.  

## Preperation

Before jumping into the demos, we must get our workstations setup and ready to go.  There are a few assumed pre-reqs you'll need to install and have functional.  

* Docker 
* Python 
* git 

> A Linux/MacOS environment is needed for the pyATS network validation demos.  You can leverage a Docker image or a VM if you are running on a Windows laptop.  

## Prep 1: Starting an Instance of Netbox on your Laptop with Docker 
It is pretty easy to start an instance of netbox right on your laptop as long as you've docker installed. Instructions from [netbox-community/netbox-docker on GitHub](https://github.com/netbox-community/netbox-docker)

1. Clone down the `netbox-docker` repo into the `netdevops_demos/source-of-truth` folder and change into it.  

	```bash
	git clone https://github.com/netbox-community/netbox-docker
	cd netbox-docker
	```

1. Hard set the port for netbox to `8081` before running `docker-compose up` by opening up the `docker-compose.yml` file and updating the ports line for nginx to set a specific port.  Netbox can run on any port... but the rest of the demo bits assume port 8081 so use it to make your life easier :-) 

	```yaml
	nginx:
	    command: nginx -c /etc/netbox-nginx/nginx.conf
	    image: nginx:1.15-alpine
	    depends_on:
	    - netbox
	    ports:
	    - 8081:8080
	```

1. This demo includes a database backup of network data that was generated with Netbox v2.5.10.  For this backup to work, we need to specify this version with this command. 

	```bash
	export VERSION=v2.5.10
	docker-compose pull netbox
	```

1. Start up netbox with docker-compose 
	
	```bash
	docker-compose up -d
	```

	* This can take a couple mintues to complete fully.  


> To stop netbox, run `docker-compose down` from the directory. 

### Verify netbox is running
1. Open up a web browser and navigate to `http://0.0.0.0:8081` (or the port you are using).  
1. You can login with `admin / admin` and look around.  You shouldn't see any data just yet.  

	![](resources/netbox_device_empty.jpg)

### Loading the Sample Source of Truth Data
Netbox starts out empty of any information.  For this demo a database backup has been provided at [resources/nb_backup.sql.gz](resources/nb_backup.sql.gz).  Now we will load up your instance of Netbox with this data. 

1. Run this command from the `netbox-docker` folder (ie `netdevops_demos/source-of-truth/netbox-docker`.)

	```bash
	gunzip -c ../resources/nb_backup.sql.gz \
		| docker exec -i $(docker-compose ps -q postgres) sh -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
	```

	* Note... the path to the backup file assumes you've followed the setup instructions in this document.  If you cloned down netbox-docker into a directory other than a subdirectory of this demo, you'll need to provide the full path to the `nb_backup.sql.gz` file.  

1. Once the command finishes, check Netbox.. you should now see devices, sites, VLANs, prefixes and more added.  

## Prep 1: Setting up your Python Environment 
Python is the go-to language for network automation, and these demos will leverage it as well.  Let's get started. 

1. Execute these steps from the `netdevops_demos/source-of-truth/` directory.

1. Start by creating a Python 3.6 (other Python 3 versions may work as well) virtual environment and activating it. 

```bash 
python3.6 -m venv venv
source venv/bin/activate 
```

1. Install the `requirements.txt` file. 

```bash 
pip install -r requirements.txt
```

# Demo's
Now that you're prepped, let's dive into the actual demo's.  

## Exploring Source of Truth Network Data
In this demo we'll take a look at the network data that has been setup in Netbox and how we can access it both through a GUI and programmatically.  

1. First, go checkout the VLANs and Prefixes in Netbox UI to see what has been setup.  
1. Now look at the Devices in Netbox.  Notice the following 
	* Devices are assigned a role.  These roles will determine which devices get L2 and L3 configurations.  For example, all switches will have VLANs configured, but routers will not.  
	* Click on `sw1` to see it's details.  Look at the interfaces that are configured.  Notice how interfaces are determined to be **Access** or **Tagged** for switchports.  And how routed interfaces have IPs configured.  Also physical interfaces have their connections indicated. 


Exploring the the UI is great, but for network automation we need this data available in code.  Let's see how that will work out next.  

1. First, be sure you have activate the python virtual environment and installed the requirements.  
1. Interacting with Netbox via the API in Python requires the url and token details.  When running in a developer instance like we've setup, this info is always the same.  We've provided a file `src_env` that will set several environment variables that will be used by our automation scripts.  Go ahead and `source` it.  

	```bash
	source src_env
	```

1. Now start up an ipython interactive session and we'll poke around at the data in Netbox via it's Python SDK.  

	```
	ipython
	```

1. Start by importing a few libraries and reading in the environment variables. 

	```python
	import pynetbox
	import os
	import ipaddress

	netbox_token = os.getenv("NETBOX_TOKEN")
	netbox_url = os.getenv("NETBOX_URL")

	site_name = os.getenv("NETBOX_SITE")
	tenant_name = os.getenv("NETBOX_TENANT")
	```

1. Create a Netbox API object.  

	```python
	netbox = pynetbox.api(netbox_url, token=netbox_token)
	```

1. Netbox is heavily setup around sites and tenants.. let's retrieve the objects for our demo.  

	```python
	tenant = netbox.tenancy.tenants.get(name=tenant_name)
	site = netbox.dcim.sites.get(name=site_name)
	```

1. Let's see what we have... 

	```python
	tenant.name 
	tenant.id 

	site.name
	site.id
	```

	1. These objects don't have a lot of data themselves, but we'll use them to search and retrieve data from Netbox.  

1. Now let's retrieve a list of devices from this site for this tenant.  

	```python
	devices = netbox.dcim.devices.filter(site_id=site.id, tenant_id=tenant.id)
	```

1. Checkout what you have.  This isn't a simple list, but each element is a device object with properties.  

	```python
	devices 
	sw1 = devices[3]
	type(sw1)
	sw1.device_type
	sw1.device_role
	```

1. Devices have interfaces, but the way the relationships are setup in Netbox, the device object doesn't "know" about it's interfaces by default in the API.  But it's pretty easy to add that data to the device.  Let's add all the interfaces for `sw1` to our object. 

	```python
	sw1.interfaces = netbox.dcim.interfaces.filter(device_id=sw1.id)

	for interface in sw1.interfaces:
		print("{}".format(interface.name))
		print("  Description: {}".format(interface.description))
		print("  dot1q Mode: {}".format(interface.mode))
	```

1. Very neat.. we have our interfaces for the device.  If we want to fill in the IP Addresses for the interfaces, we can do that with this bit of code.  

	```python
	for interface in sw1.interfaces:
		interface.ip_addresses = netbox.ipam.ip_addresses.filter(interface_id=interface.id)

	for interface in sw1.interfaces:
		print("{}".format(interface.name))
		print("  Description: {}".format(interface.description))
		print("  dot1q Mode: {}".format(interface.mode))
		if interface.ip_addresses: 
			print("  IP Addresses: {}".format(interface.ip_addresses))
	```

1. And if we want to pull the VLANs and related Prefixes into Python, we can do so with this code.  

	```python
	# Get VLAN Info from Netbox
	vlans = netbox.ipam.vlans.filter(site_id=site.id)

	# Retrieve Prefixes for VLANs
	for vlan in vlans:
		vlan.prefix = netbox.ipam.prefixes.get(vlan_id=vlan.id)

	# Print out some bits
	for vlan in vlans: 
		print("VLAN: {} ({})".format(vlan.vid, vlan.name))
		print("  Description: {}".format(vlan.description))
		print("  Prefix: {}".format(vlan.prefix))
	```

Now you can see how the source of truth data can be accessed.. let's put it to use!  

## Source of Truth Driven Configuration Templates 
In this demo we'll see how we can generate consistent network configuration templates based on the data in the source of truth.  Specifically we'll look at generating VLAN and Interface Configurations.  

1. The idea is to use the information from the source of truth about the specifics and combine them with the templates defined and developed by network architects and engineers. 
1. Take a look at the files Jinja templates in the `templates` directory.  These indicate how VLANs and interfaces should be configured given a set of data.  For example, here is `templates/vlan_configuration.j2`. 

	```jinja
	! VLAN Configurations 
	{% for vlan in vlans -%}
	vlan {{ vlan.vid }}
	name {{ vlan.name }}
	{% endfor -%}
	```

	* For a list of VLANS from the source of truth, we will generate a VLAN CLI configuration.  

1. The actual code that combines the Netbox data with the templates is in the file `build_configs.py`.  It leverages the same Python code we used earlier to pull information from Netbox, and then uses standard Jinja template code to build configs.  Let's run the script.  

	```
	python build_configs.py

	# Partial Output
	Device rtr1 of role Edge Router
	- Building Interface Configurations for Device
	Device sw1 of role Distribution Switch
	- Building L2 VLAN Configuration for Device
	- Building Interface Configurations for Device
	```

1. Look in the folder `configs/` where you'll now find the newly generated configurations.  Take a look at them and compare them to what you'd expect from the source of truth and tempaltes. 

	```bash
	$ls -l configs/
	total 28
	-rw-rw-r-- 1 developer developer  680 Aug 19 19:56 rtr1.cfg
	-rw-rw-r-- 1 developer developer  676 Aug 19 19:56 rtr2.cfg
	-rw-rw-r-- 1 developer developer  677 Aug 19 19:56 rtr3.cfg
	-rw-rw-r-- 1 developer developer 1746 Aug 19 19:56 sw1.cfg
	-rw-rw-r-- 1 developer developer 1802 Aug 19 19:56 sw2.cfg
	-rw-rw-r-- 1 developer developer  759 Aug 19 19:56 sw3.cfg
	-rw-rw-r-- 1 developer developer  759 Aug 19 19:56 sw4.cfg
	```

1. The idea would be to then apply these configurations to the network devices. 

	> For this demonstration, we don't have a running network on which to apply these configurations.  

## Validating that the Network Matches the Source of Truth 
A Source of Truth isn't only valuable for creating network configurations, it is equally useful for verifying the network is operating how you intend it to be.  

Suppose for an example you wanted to make sure that all the VLANs that were suposed to be configured were actually configured on all the switches?  Or that all the interfaces that were supposed to be up, were up.  And the ones that should be access ports were indeed access ports in the correct VLAN? How would you do it? 

Odds are you'd connect to the network and run a bunch of show commands, and verify the output matched what you "knew" it was supposed to be.  Well, can't we automate that?  

For our demo, the Source of Truth replaces what we "know", with something that is far more likely to be accurate.  And our method for running the show commands will be to leverage [pyATS and Genie](https://developer.cisco.com/pyats), the open source network validation and testing tool from Cisco.  

## Basic Python Validation Script 
For this first demonstration we will see how we can use the pyATS/Genie libraries within in a Python script to learn about the operational state of our network and compare that to what we know we can get out of Netbox.  

1. Don't forget to `source srv_env` if you've closed your terminal. 

1. Go ahead and start up `ipython` again as we'll work interactively for this example. 

	```
	ipython
	```

1. First up, let's pull in the details from Netbox about our network.  In the repository a python module called `get_from_netbox.py` is provided that queries Netbox and returns a `devices` and `vlans` list containing the details for testing.  Let's import that file.  

	```python
	from get_from_netbox import devices, vlans

	devices
	vlans
	```

1. Import Genie. 

	```python
	from genie.conf import Genie
	```

1. pyATS and Genie need a `testbed` to know what network to connect to.  For this demo, a simulated network that matches the source of truth is included, and the testbed for it is `genie/demo_testbed.yaml`. 

	```python
	testbed = Genie.init("genie/demo_testbed.yaml")
	```

1. For this demo we are only going to explore the state of `sw1`. Let's connect to it.  
	* We are silencing the logging of connection info.  If you'd like to see all the interactions with each device, you can remove `log_stdout=False` from the command. 

	```python
	device = testbed.devices["sw1"]
	device.connect(log_stdout=False)
	```

1. Now that we are connected we can `learn` about the VLANs using Genie.  

	```python
	device.vlans = device.learn("vlan")

	device.vlans.info
	```

1. What we want to do is compare the `set` of VLANs from Netbox to what is actually configured.  Python `set` objects make this type of comparison really easy.  Let's create a set of VLAN IDs and Names from netbox.  

	```python
	nb_vlan_set = set([(vlan.vid, vlan.name) for vlan in vlans])

	nb_vlan_set
	```

1. Next up we need to create a set of the VLANs from the device.  

	```python
	device_vlan_set = set(
				[
					(int(vid), details["name"])
					for vid, details in device.vlans.info["vlans"].items()
				]
			)

	device_vlan_set		
	```

	> These two commands are using list comprehension from Python to quickly create a list of Tuples and then convert that to a set.

1. With the two sets created, let's see if any vlans are missing or extra. 

	```python
	missing_vlans = nb_vlan_set.difference(device_vlan_set)

	print("Missing VLANs: ", missing_vlans)

	extra_vlans = device_vlan_set.difference(nb_vlan_set)

	print("Extra VLANS: ", extra_vlans)
	```

1. Well... we don't really care about all those internal VLANs.. let's pull them out by creating an additional set and subtracting them.  

	```python
	internal_vlans = {
		(1003, "token-ring-default"),
		(1, "default"),
		(1002, "fddi-default"),
		(1005, "trnet-default"),
		(1004, "fddinet-default"),
	}
	extra_vlans = extra_vlans.difference(internal_vlans)

	print("Extra VLANS: ", extra_vlans)
	```

1. Cool... now let's repeat for `sw2`.  

	```python
	device = testbed.devices["sw2"]
	device.connect(log_stdout=False)
	device.vlans = device.learn("vlan")
	device_vlan_set = set(
				[
					(int(vid), details["name"])
					for vid, details in device.vlans.info["vlans"].items()
				]
			)
	missing_vlans = nb_vlan_set.difference(device_vlan_set)
	extra_vlans = device_vlan_set.difference(nb_vlan_set).difference(internal_vlans)

	print("Missing VLANs: ", missing_vlans)

	print("Extra VLANS: ", extra_vlans)
	```

1. Pretty neat right!   Go ahead and `exit()` from python.

## Building Network Test Cases with pyATS and Genie
While you can do a lot with Python scripts like the above, what you really need is a way to build robust network tests that can be executed and reported on.  pyATS offers a robust framework for creating such tests.  Let's checkout a basic exmample.  

> Exploring the details of test case creation is beyond the scope of this demo, but let's run them anyway!  

1. In the `tests/` folder there is a `vlan.py` and an `interface.py` file.  Each is a pyATS Test Script that will compare the data from Netbox to the network.  
1. Run the VLAN test. 

	```
	python tests/vlan.py --testbed genie/demo_testbed.yaml
	```

1. Take a look at the output.. did any switches passed?  If any failed, why?  

1. Now let's run the `interace.py` test.  

	```
	python tests/interface.py --testbed genie/demo_testbed.yaml
	```

1. What are the results of this test?  What failed and why?  