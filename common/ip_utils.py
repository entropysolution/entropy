import ipcalc

def in_subnets(remote_addr, subnets):
    for subnet in subnets:
        if remote_addr in ipcalc.Network(subnet):
            return True
    return False
