#! /bin/bash

echo "This is a simple bash script to highlight some example commands and structure."
echo ""

echo "Let's wait until an API returns a 200 OK"
echo ""

echo "Checking if the DevNet IOS XE Always On RESTCONF device is up."
echo "If it isn't, check again in 30 seconds (for max of 5 minutes)"

echo "We're using a bash function and while loop to check until ready."
echo ""

# Function to get the status code
get_status_code() {
code=$(curl -ks \
-w "%{http_code}" \
-o /dev/null \
-u 'root:D_Vay!_10&' \
-H "Accept: application/yang-data+json" \
"https://ios-xe-mgmt.cisco.com:9443/restconf/data/ietf-interfaces:interfaces"
)
echo $code
}

# Initial check of status_code
status_code=$(get_status_code)

# Initializing counter at 0
COUNTER=0

# Loop until status code is 200, or 10 tries
while [ $status_code -ne 200 -a $COUNTER -lt 10 ]; do
echo "Not ready yet, waiting 30 seconds and trying again."
sleep 30
status_code=$(get_status_code)
COUNTER=$(($COUNTER+1))
done

if [ $status_code -eq 200 ]
then
  echo "✅ Yep, it's up and returning a 200. "
else
  echo "❌ Nope, it returned a $status_code"
fi
