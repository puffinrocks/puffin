import ipaddress

import docker.types


def init():
    pass

def get_next_cidr(client):
    networks = client.networks.list()
    last_cidr = ipaddress.ip_network("10.0.0.0/24")
    for network in networks:
        if (network.attrs["IPAM"] and network.attrs["IPAM"]["Config"]
                and len(network.attrs["IPAM"]["Config"]) > 0
                and network.attrs["IPAM"]["Config"][0]["Subnet"]):
            cidr = ipaddress.ip_network(network.attrs["IPAM"]["Config"][0]["Subnet"])
            if cidr.network_address.packed[0] == 10:
                if cidr.prefixlen != 24:
                    raise Exception(
                            "Invalid network prefix length {0} for network {1}"
                            .format(cidr.prefixlen, network.name))
                if cidr > last_cidr:
                    last_cidr = cidr

    next_cidr = ipaddress.ip_network((last_cidr.network_address + 256).exploded + "/24")
    if next_cidr.network_address.packed[0] > 10:
        raise Exception("No more networks available")
    last_cidr = next_cidr
    return next_cidr

def create_network(client, name):
    cidr = get_next_cidr(client)
    print("Creating network {0} with subnet {1}".format(name, cidr.exploded))

    networks = client.networks.list(names=[name])
    if len(networks) > 0:
        for network in networks:
            network.remove()

    ipam_pool = docker.types.IPAMPool(subnet=cidr.exploded,
            gateway=(cidr.network_address + 1).exploded)
    ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
    client.networks.create(name, ipam=ipam_config)
