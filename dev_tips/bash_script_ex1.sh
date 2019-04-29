#! /bin/bash

echo "This is a simple bash script to highlight some example commands and structure."
echo ""

echo "Let's see if a REST API is up and responding as expected."
echo "  That is, does it return a '200 OK'"
echo ""

echo "Checking if the DevNet IOS XE Always On RESTCONF device is up."

status_code=$(curl -ks \
-w "%{http_code}" \
-o /dev/null \
-u 'root:D_Vay!_10&' \
-H "Accept: application/yang-data+json" \
"https://ios-xe-mgmt.cisco.com:9443/restconf/data/ietf-interfaces:interfaces"
)

if [ $status_code -eq 200 ]
then
  echo "✅ Yep, it's up and returning a 200. "
else
  echo "❌ Nope, it returned a $status_code"
fi
