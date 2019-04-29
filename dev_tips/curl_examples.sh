# A series of example curl commands

# 1. Connect to a REST API and retrieve the data
#   -k  Allow untrusted certs
#   -u  Provide user:password for Basic Authentication
#   -H  Add a header
curl -k \
-u 'root:D_Vay!_10&' \
-H "Accept: application/yang-data+json" \
"https://ios-xe-mgmt.cisco.com:9443/restconf/data/ietf-interfaces:interfaces"

# 2. Just retrieve the headers and throw away the data
#   -v  "Verbose" output
#   -o /dev/null  Save output to a file - /dev/null to throw away
curl -vk \
-o /dev/null \
-u 'root:D_Vay!_10&' \
-H "Accept: application/yang-data+json" \
"https://ios-xe-mgmt.cisco.com:9443/restconf/data/ietf-interfaces:interfaces"

# 3. Just retrieve the status code
#   -s "Silent mode"      don't output extra stuff (like transfer stats)
#   -w "%{http_code}"     Output formating (see man curl for details)
curl -ks \
-w "%{http_code}" \
-o /dev/null \
-u 'root:D_Vay!_10&' \
-H "Accept: application/yang-data+json" \
"https://ios-xe-mgmt.cisco.com:9443/restconf/data/ietf-interfaces:interfaces"

# 4. Retrieve a specific value from a JSON payload
#   | python -c 'python code'  Send output of curl as input to Python one liner
curl -sk \
-u 'root:D_Vay!_10&' \
-H "Accept: application/yang-data+json" \
"https://ios-xe-mgmt.cisco.com:9443/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet1" \
| python -c 'import sys, json;
print(
  json.load(sys.stdin)["ietf-interfaces:interface"]["ietf-ip:ipv4"]["address"][0]["ip"]
  )'
