from ipaddress import ip_network
from docker.utils import create_ipam_pool, create_ipam_config


def init():
    pass

def get_next_cidr(client):
    networks = client.networks()
    last_cidr = ip_network("10.0.0.0/24")
    for network in networks:
        if (network["IPAM"] and network["IPAM"]["Config"] 
                and len(network["IPAM"]["Config"]) > 0
                and network["IPAM"]["Config"][0]["Subnet"]):
            cidr = ip_network(network["IPAM"]["Config"][0]["Subnet"])
            if cidr.network_address.packed[0] == 10:
                if cidr.prefixlen != 24:
                    raise Exception(
                            "Invalid network prefix length {0} for network {1}"
                            .format(cidr.prefixlen, network["Name"]))
                if cidr > last_cidr:
                    last_cidr = cidr
    
    next_cidr = ip_network((last_cidr.network_address + 256).exploded + "/24")
    if next_cidr.network_address.packed[0] > 10:
        raise Exception("No more networks available")
    last_cidr = next_cidr
    return next_cidr

def create_network(client, name):
    cidr = get_next_cidr(client)
    print("Creating network {0} with subnet {1}".format(name, cidr.exploded))
    
    networks = client.networks(names=(name,))
    if len(networks) > 0:
        for network in networks:
            client.remove_network(name)
    
    ipam_pool = create_ipam_pool(
            subnet=cidr.exploded, gateway=(cidr.network_address + 1).exploded)
    ipam_config = create_ipam_config(pool_configs=[ipam_pool])
    client.create_network(name, ipam=ipam_config)
