import random
import time
import struct
import socket
import binascii

def mac_addr(mac_add_bytes):
    # convert the bytes to string
    return ':'.join(map('{:02x}'.format, mac_add_bytes)).upper()


def ethernet_frame(data):
    dest_mac, src_mac, eth_protocol = struct.unpack('!6s6sH', data[:14])
    return mac_addr(dest_mac), mac_addr(src_mac), socket.htons(eth_protocol), data


def ipv4_packet(ip_header):
    iph = struct.unpack('!BBHHHBBH4s4s', ip_header[:20])

    version_ihl = iph[0]
    version = version_ihl >> 4

    ih_len = (version_ihl & 0xF) * 4
    ttl = iph[5]
    protocol = iph[6]

    s_addr = socket.inet_ntoa(iph[8])
    d_addr = socket.inet_ntoa(iph[9])

    return s_addr, d_addr, protocol, ip_header[ih_len:]


def icmp_packet(data):
    icmp_type, code, checksum = struct.unpack('!BBH', data[:4])
    if icmp_type == 0:
        type_status = "0 (Echo Reply)"
    elif icmp_type == 8:
        type_status = "8 (Echo Request)"
    return (icmp_type, type_status), code, checksum, data[4:]


def tcp_packet(packet_buffer):
    tcp_raw_data = struct.unpack("!2s2s4s4s2s2s2s2s", packet_buffer)
    src_port = binary_to_ascii(tcp_raw_data[0])
    dst_port = binary_to_ascii(tcp_raw_data[1])

    return int(src_port, 16), int(dst_port, 16)

def binary_to_ascii(binary_data):
    return binascii.hexlify(binary_data).decode("utf-8")

def udp_packet(data):
    src_port, dest_port, size = struct.unpack('!HH2xH', data)
    return src_port, dest_port, size, data[8:]


def arp_packet(arp_header):
    arph = struct.unpack("!2s2s1s1s2s6s4s6s4s", arp_header)

    # convert bytes to hex and then decode it as string
    protocol_size = binascii.hexlify(arph[3]).decode('utf-8')
    protocol_type = binascii.hexlify(arph[1]).decode('utf-8')

    # get the mac address bytes and convert it to a string
    src_mac = mac_addr(arph[5])
    dst_mac = mac_addr(arph[7])

    # get the ip bytes and convert it to an IP string
    src_ip = socket.inet_ntoa(arph[6])
    dst_ip = socket.inet_ntoa(arph[8])

    return src_ip, dst_ip, src_mac, dst_mac, protocol_type, protocol_size


def ipv6_packet(data):
    ipv6_first_word, payload_legth, protocol, hoplimit = struct.unpack(">IHBB", data[0:8])
    src_ip = socket.inet_ntop(socket.AF_INET6, data[8:24])
    dst_ip = socket.inet_ntop(socket.AF_INET6, data[24:40])

    version = ipv6_first_word >> 28
    traffic_class = int(ipv6_first_word >> 16) & 4095
    flow_label = int(ipv6_first_word) & 65535

    return src_ip, dst_ip, protocol, data[40:]
