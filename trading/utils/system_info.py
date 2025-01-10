import socket
import uuid

def get_system_info():
    """Get system's IP and MAC address"""
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                   for elements in range(0,2*6,2)][::-1])
    return local_ip, mac