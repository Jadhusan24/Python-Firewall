import socket
import time
import threading
from netaddr import IPNetwork
import psutil
import csv
import datetime
import logging


# Custom imports
from imports.protocols import ethernet_frame, ipv4_packet, icmp_packet, udp_packet, tcp_packet
from imports.helper import get_interfaces, pprint, compare_rules, PROTOCOLS
from imports.validator import validate_with_route_table


logging.basicConfig(level=logging.INFO, filename="firewall.log", filemode="w")

# Create Send Socket for all the interfaces
send_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)


def sendpacket(conn: socket.socket, payload, dst_ip):
    try:
        conn.sendto(payload, (dst_ip, 0))
    except PermissionError as broadcastError:
        print(broadcastError)
        pass
    except OSError as Error:
        print(Error)
        pass


def bind_sockets(interface):
    # create a socket connection to listen for packets
    conn = socket.socket(socket.AF_PACKET, socket.SOCK_RAW,socket.ntohs(0x0800))
    conn.bind((interface[0], 0))
    try:
        while True:
            # continuously receive/listen for data
            # send(bytes[, flags])
            raw_data, _ = conn.recvfrom(65536)
            # create a new Ethernet instance with the raw_data captured
            dest_mac, src_mac, eth_protocol, eth_data = ethernet_frame(raw_data)  # gather the frame details
            src_port, dst_port = 0, 0
            if eth_protocol == 8:
                s_addr, d_addr, protocol, ip_header = ipv4_packet(eth_data[14:34])
                logging.info(f"[{datetime.datetime.now()}] {interface[0]} ({d_addr}) >  {PROTOCOLS[protocol]}")
                if protocol == 6:
                    # Extract the TCP dst & src Ports
                    src_port, dst_port = tcp_packet(eth_data[34:54])

                elif protocol == 17:
                    # Extract the UDP dst & src Ports
                    src_port, dest_port, size, data = udp_packet(eth_data[34:42])
                # BY DEFAULT ALL TRAFFIC IS DENIED. 
                # ANY ROUTES IN THE RULES FILE WILL BE ALLOWED
                if validate_with_route_table(s_addr, d_addr, src_port, dst_port):
                    sendpacket(send_sock, eth_data[14:], d_addr)
                else:
                    logging.error(f"<FAILED ROUTE>[{datetime.datetime.now()}] {interface[0]} ({s_addr}, {d_addr}) >  {PROTOCOLS[protocol]}")
                    # print(f"[ERR] Route is either denied or invalid! {interface[0]} ({s_addr}:{src_port}, {d_addr}:{dst_port}) >  {PROTOCOLS[protocol]}")
    except KeyboardInterrupt:
        print("\n[END] STOPPED")
        return


if __name__ == "__main__":
    interfaces = get_interfaces()

    if len(interfaces.items()) < 4:
        print("Not enough interfaces")
        exit()
    for key, val in interfaces.items():
        tr = threading.Thread(target=bind_sockets,args=([key, val],), name=key)
        tr.setDaemon(True)
        tr.start()
    print("FIREWALL IS RUNNING ")
    try:
        while True:
            for _ in range(10):
                time.sleep(.2)
    except KeyboardInterrupt:
        print("\nEXITING FIREWALL")
        exit(1)
