"""
ESP-NOW Helper Library for MicroPython
Simplified ESP-NOW communication with automatic peer management
"""

import network
import espnow
import json
import struct
from machine import unique_id
import ubinascii

class ESPNowHelper:
    def __init__(self, channel=1):
        """
        Initialize ESP-NOW helper
        
        Args:
            channel: WiFi channel (1-13)
        """
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.config(channel=channel)
        
        self.esp_now = espnow.ESPNow()
        self.esp_now.active(True)
        
        self.peers = {}
        self.receive_callback = None
        
        # Get own MAC address
        self.mac = self.wlan.config('mac')
        self.mac_str = ubinascii.hexlify(self.mac, ':').decode()
        
    def add_peer(self, mac_address, name=None):
        """
        Add a peer device
        
        Args:
            mac_address: MAC address as bytes or string
            name: Optional peer name for identification
        """
        if isinstance(mac_address, str):
            # Convert string MAC to bytes
            mac_bytes = ubinascii.unhexlify(mac_address.replace(':', ''))
        else:
            mac_bytes = mac_address
            
        self.esp_now.add_peer(mac_bytes)
        
        if name:
            self.peers[mac_bytes] = name
        
        return mac_bytes
    
    def remove_peer(self, mac_address):
        """Remove a peer device"""
        if isinstance(mac_address, str):
            mac_bytes = ubinascii.unhexlify(mac_address.replace(':', ''))
        else:
            mac_bytes = mac_address
            
        self.esp_now.del_peer(mac_bytes)
        if mac_bytes in self.peers:
            del self.peers[mac_bytes]
    
    def send_data(self, data, mac_address=None):
        """
        Send data to peer(s)
        
        Args:
            data: Data to send (dict will be JSON encoded)
            mac_address: Target MAC (None for broadcast)
        
        Returns:
            bool: Success status
        """
        try:
            if isinstance(data, dict):
                # JSON encode dictionaries
                payload = json.dumps(data).encode('utf-8')
            elif isinstance(data, str):
                payload = data.encode('utf-8')
            else:
                payload = data
            
            if mac_address:
                if isinstance(mac_address, str):
                    mac_bytes = ubinascii.unhexlify(mac_address.replace(':', ''))
                else:
                    mac_bytes = mac_address
                return self.esp_now.send(mac_bytes, payload)
            else:
                # Broadcast to all peers
                return self.esp_now.send(None, payload)
                
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def send_struct(self, data_struct, format_string, mac_address=None):
        """
        Send structured data using struct format
        
        Args:
            data_struct: Tuple/list of data to pack
            format_string: Struct format string (e.g., 'ffff' for 4 floats)
            mac_address: Target MAC (None for broadcast)
        """
        try:
            payload = struct.pack(format_string, *data_struct)
            
            if mac_address:
                if isinstance(mac_address, str):
                    mac_bytes = ubinascii.unhexlify(mac_address.replace(':', ''))
                else:
                    mac_bytes = mac_address
                return self.esp_now.send(mac_bytes, payload)
            else:
                return self.esp_now.send(None, payload)
                
        except Exception as e:
            print(f"Struct send error: {e}")
            return False
    
    def receive_data(self, timeout_ms=100):
        """
        Receive data from ESP-NOW
        
        Args:
            timeout_ms: Receive timeout in milliseconds
            
        Returns:
            tuple: (sender_mac, data) or (None, None) if timeout
        """
        try:
            host, msg = self.esp_now.recv(timeout_ms)
            if host and msg:
                # Try to decode as JSON first
                try:
                    data = json.loads(msg.decode('utf-8'))
                    return host, data
                except:
                    # Return raw bytes if not JSON
                    return host, msg
            return None, None
        except:
            return None, None
    
    def receive_struct(self, format_string, timeout_ms=100):
        """
        Receive structured data
        
        Args:
            format_string: Struct format string
            timeout_ms: Receive timeout
            
        Returns:
            tuple: (sender_mac, unpacked_data) or (None, None)
        """
        try:
            host, msg = self.esp_now.recv(timeout_ms)
            if host and msg:
                try:
                    data = struct.unpack(format_string, msg)
                    return host, data
                except:
                    return host, msg
            return None, None
        except:
            return None, None
    
    def set_receive_callback(self, callback):
        """
        Set callback function for received messages
        Callback signature: callback(sender_mac, data)
        """
        self.receive_callback = callback
    
    def check_messages(self):
        """Check for incoming messages and call callback if set"""
        if self.receive_callback:
            host, data = self.receive_data(0)  # Non-blocking
            if host and data:
                peer_name = self.peers.get(host, ubinascii.hexlify(host, ':').decode())
                self.receive_callback(host, data, peer_name)
    
    def get_mac_address(self):
        """Get own MAC address as string"""
        return self.mac_str
    
    def get_peers(self):
        """Get list of added peers"""
        return list(self.peers.keys())
    
    def deinit(self):
        """Cleanup ESP-NOW resources"""
        self.esp_now.active(False)
        self.wlan.active(False)

    def recv_jikken_start(self, peer):
        print("wait start")
        mac_bytes = ubinascii.unhexlify(peer.replace(':', ''))
        while True:
            host, msg = self.esp_now.recv()
            if host == mac_bytes:
                return
            
    def send_jikken_start(self, peer):
        print("send jikken start")
        while True:
            success = self.send_data("jikken_start", peer)
            if success == True:
                return