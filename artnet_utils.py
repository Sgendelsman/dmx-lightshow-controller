from project_config import *

import socket
import struct
import time

# Create UDP socket once
artnet_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_dmx(universe, values: dict):
    """Send ArtDMX packet with channel-value dictionary"""
    print(f"[{time.perf_counter():.3f}] DMX -> {values}")
    dmx_data = [0] * 512
    for ch, val in values.items():
        if 1 <= ch <= 512:
            dmx_data[ch - 1] = val

    packet = build_artdmx_packet(universe, dmx_data)
    artnet_socket.sendto(packet, (ARTNET_IP, ARTNET_PORT))

def build_artdmx_packet(universe, dmx_data):
    """Builds a standard ArtDMX packet"""
    if len(dmx_data) > 512:
        raise ValueError("DMX data too long")

    # Header
    packet = bytearray()
    packet.extend(b'Art-Net\x00')                     # Art-Net ID
    packet.extend(struct.pack('<H', 0x5000))          # OpCode: ArtDMX (little endian)
    packet.extend(struct.pack('>H', 14))              # Protocol version (big endian: 14)
    packet.append(0x00)                               # Sequence
    packet.append(0x00)                               # Physical
    packet.extend(struct.pack('<H', universe))        # Universe (little endian)
    packet.extend(struct.pack('>H', len(dmx_data)))   # Length (big endian)
    packet.extend(bytearray(dmx_data))                # DMX data

    return packet