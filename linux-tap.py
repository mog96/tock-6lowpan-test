import fcntl
import os
import struct
import subprocess
from time import sleep

# Some constants used to ioctl the device file. I got them by a simple C
# program.
TUNSETIFF = 0x400454ca
TUNSETOWNER = TUNSETIFF + 2
IFF_TUN = 0x0001
IFF_TAP = 0x0002
IFF_NO_PI = 0x1000

# Open file corresponding to the TUN device.
tap = open('/dev/net/tun', 'r+b')
ifr = struct.pack('16sH', 'tap0', IFF_TAP | IFF_NO_PI)
fcntl.ioctl(tap, TUNSETIFF, ifr)
fcntl.ioctl(tap, TUNSETOWNER, 1000)

# Bring it up and assign addresses.
subprocess.check_call('ifconfig tap0 192.168.7.1 pointopoint 192.168.7.2 up',
        shell=True)
# subprocess.check_call('ifconfig tap0 inet6 2001:0db8:85a3:0000:0000:8a2e:0370:7334/64 pointopoint fe80::f8ca:a929:6861:653b/64 up',
#         shell=True)

while True:
    # Read an IP packet been sent to this TUN device.
    packet = list(os.read(tap.fileno(), 2048))

    print ''.join(packet)

    # Modify it to an ICMP Echo Reply packet.
    #
    # Note that I have not checked content of the packet, but treat all packets
    # been sent to our TUN device as an ICMP Echo Request.

    # Swap source and destination address.
    # packet[12:16], packet[16:20] = packet[16:20], packet[12:16]

    # Under Linux, the code below is not necessary to make the TUN device to
    # work. I don't know why yet. If you run tcpdump, you can see the
    # difference.
    # if True:
    #     # Change ICMP type code to Echo Reply (0).
    #     packet[20] = chr(0)
    #     # Clear original ICMP Checksum field.
    #     packet[22:24] = chr(0), chr(0)
    #     # Calculate new checksum.
    #     checksum = 0
    #     # for every 16-bit of the ICMP payload:
    #     for i in range(20, len(packet), 2):
    #         half_word = (ord(packet[i]) << 8) + ord(packet[i+1])
    #         checksum += half_word
    #     # Get one's complement of the checksum.
    #     checksum = ~(checksum + 4) & 0xffff
    #     # Put the new checksum back into the packet.
    #     packet[22] = chr(checksum >> 8)
    #     packet[23] = chr(checksum & ((1 << 8) -1))

    # Write the reply packet into TUN device.
    os.write(tap.fileno(), ''.join(packet))
    # os.write(tap.fileno(), "testing")

    # sleep(2)