import csv
import os
import getpass
import requests

# Should be set appropriately for the network environment.
SCHEME = 'http'
PORT = 3000

SINGLE_RPC_URL_FORMAT = SCHEME + '://%s:' + str(PORT) + '/rpc/%s@format=%s'
# MULTIPLE_RPC_URL_FORMAT = SCHEME + '://%s:' + str(PORT) + '/rpc'

def get_ospf_neighbor(host, user, pwd):
    url = SINGLE_RPC_URL_FORMAT % (host, 'get-ospf-neighbor-information', 'json')
    http_response = requests.get(url, auth=(user,pwd))
    http_response.raise_for_status()    # raise_for_status() method causes an exception to be raised if any HTTP status code other than 200 OK is returned.

    if http_response.headers['Content-type'].startswith('application/xml'):
        _ = check_for_warning_and_errors(parser(http_response.text))
        return None

    resp = http_response.json()

    ospf_info = {}

    try:
        neighbor_info = resp['ospf-neighbor-information'][0]['ospf-neighbor']
    except KeyError:
        return None

    for neighbor in neighbor_info:
        try:
            nbr_addr = neighbor['neighbor-address'][0]['data']
            nbr_if_name = neighbor['interface-name'][0]['data']
            nbr_state = neighbor['ospf-neighbor-state'][0]['data']
            ospf_info[host] = {'Neighbor Address': nbr_addr,
                               'Neighbor Interface': nbr_if_name,
                               'Neighbor state': nbr_state}
        except KeyError:
            return None

    return ospf_info

def mergedict(a,b):
    a.update(b)
    print(a)
    return a

with open('ipfile.txt') as ip:
    hostnames = ip.readlines()

username = input("Enter your username: ").strip()
password = getpass.getpass("Password: ").strip()

for hostname in hostnames:
    host = hostname.strip()
    print(f"Getting ospf information from {hostname}")
    ospf_info = get_ospf_neighbor(host=host, user=username, pwd=password)
    # print(ospf_info)
    file_exists = os.path.isfile('ospf_neighbor-data.csv')
    fields = ['Local-Router', 'Neighbor Address', 'Neighbor Interface', 'Neighbor state']
    with open('ospf_neighbor-data.csv', 'a', newline='') as file:
        csv_writer = csv.DictWriter(file, fields)
        if not file_exists:
            csv_writer.writeheader()
        for k, d in ospf_info.items():
            csv_writer.writerow(mergedict({'Local-Router': k},d))






