# SHELL := /bin/bash
PROJECT_DIR := $(shell pwd)
VIRL_ID := $(shell virl id)


# virl: 
#   -@virl up --provision virlfiles/ccnx_study 

# netbox: 
#   -@export PROJECT_DIR=$(pwd)
#   -@cd ~/code/netbox-docker 
#   -@docker-compose up -d 
#   -cd $PROJECT_DIR

virl-to-netbox: 
	-@cd ../pyats-to-netbox && \
		virl use ${VIRL_ID} && \
		virl generate pyats && \
		PYATS_USERNAME=cisco PYATS_PASSWORD=cisco PYATS_AUTH_PASS=cisco ./load_netbox.py 

