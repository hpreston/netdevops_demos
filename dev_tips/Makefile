SHELL := /bin/bash

export PYATS_USERNAME=cisco
export PYATS_PASSWORD=cisco
export PYATS_AUTH_PASS=cisco

dev: virl nso virl-generate nso-sync-from genie-learn

clean: nso-clean virl-clean genie-clean

virl:
	@echo "Starting the VIRL topology, and waiting for it to be ready"
	-@virl up --provision --wait-time 10 virlfiles/2-ios-router
	@sleep 90

virl-generate:
	@echo "Adding network devices to nso and creating pyATS testbed"
	-@virl generate nso
	-@virl generate pyats

virl-clean:
	@echo "Tearing down VIRL topology."
	-@virl down
	-@rm -Rf default_testbed.yaml .virl/ topology.virl

nso:
	@echo "Setting up NSO dev instance."
	@ncs-setup --package cisco-ios --dest .
	@ncs

nso-clean:
	@echo "Destroying NSO dev instance."
	-@ncs --stop
	-@rm -Rf README.ncs agentStore state.yml logs/ ncs-cdb/ ncs-java-vm.log ncs-python-vm.log ncs.conf state/ storedstate target/ packages/ scripts/

nso-sync-from:
	@echo "Syncing network configuration to NSO."
	-@curl -X POST -u admin:admin http://localhost:8080/api/running/devices/_operations/sync-from

genie-learn:
	@echo "Learning interface from network with genie."
	@genie learn interface --testbed default_testbed.yaml --output learned/

genie-clean:
	@echo "Deleting genie files"
	-@rm -Rf learned/
