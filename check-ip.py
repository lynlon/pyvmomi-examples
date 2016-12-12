import socket,sys

def is_valid_ip(ip):
    """Returns true if the given string is a well-formed IP address. 
 
    Supports IPv4.
    """
    if len(ip.split('.')) < 4:return False
    if not ip or '\x00' in ip:
        # getaddrinfo resolves empty strings to localhost, and truncates  
        # on zero bytes.  
        return False
    try:
        res = socket.getaddrinfo(ip, 0, socket.AF_UNSPEC,
                                 socket.SOCK_STREAM,
                                 0, socket.AI_NUMERICHOST)
        return bool(res)
    except socket.gaierror as e:
        if e.args[0] == socket.EAI_NONAME:
            return False
        raise
    return True
