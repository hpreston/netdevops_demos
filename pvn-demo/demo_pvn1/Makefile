clean:
	- ncs --stop
	- sudo killall confd
	- virl down
	- rm -Rf .virl
	- rm -Rf README.ncs
	- rm -Rf agentStore
	- rm -Rf default_testbed.yaml
	- rm -Rf logs
	- rm -Rf ncs-cdb
	- rm -Rf ncs.conf
	- rm -Rf packages
	- rm -Rf scripts
	- rm -Rf state
	- rm -Rf state.yml
	- rm -Rf target

prep:
	- virl up --provision virlfiles/5_router_mesh
	- ncs-setup --package cisco-ios --dest .
	- ncs
	- virl generate nso
	# API call to sync from 
	# API call to create device group
	# API call to create configuratin template
	#
