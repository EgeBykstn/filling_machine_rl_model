"""
TCP client for receiving real filling data from physical device.
"""

import socket
import time
import logging
from typing import Optional
from config import DEFAULT_TCP_TIMEOUT


class TCPClient:
    """TCP client for receiving filling data from physical device."""
    
    def __init__(self, ip: str, port: int, timeout: float = DEFAULT_TCP_TIMEOUT):
        """
        Initialize TCP client.
        
        Args:
            ip: Device IP address
            port: Device TCP port
            timeout: Timeout in seconds for receiving data
        """
        self.ip = ip
        self.port = port
        self.client_socket = None
        self.timeout = timeout
        
    def connect(self) -> bool:
        """
        Connect to the TCP device.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.ip, self.port))
            self.client_socket.settimeout(self.timeout)
            logging.info(f"Connected to TCP device at {self.ip}:{self.port}")
            
            # Send test message to initialize connection
            self._send_test_message()
            return True
            
        except Exception as e:
            logging.error(f"Failed to connect to TCP device: {e}")
            self.client_socket = None
            return False
    
    def _send_test_message(self) -> None:
        """Send initial test message to device."""
        try:
            message = "test"
            self.client_socket.sendall(message.encode('ascii'))
            logging.info(f"Sent test message: {message}")
        except Exception as e:
            logging.error(f"Failed to send test message: {e}")
    
    def receive_data(self) -> Optional[str]:
        """
        Receive filling episode data from device.
        
        Returns:
            Raw data string if received, None if timeout or error
        """
        if not self.client_socket:
            logging.error("TCP client not connected")
            return None
            
        buffer = []
        last_received_time = time.time()
        
        while True:
            try:
                data = self.client_socket.recv(4096)
                if data:
                    buffer.append(data.decode('ascii'))
                    last_received_time = time.time()  # Reset timer
                else:
                    break  # End of transmission
                    
            except socket.timeout:
                if (time.time() - last_received_time) > self.timeout:
                    logging.info("TCP timeout reached, episode complete")
                    break
                continue
                
            except Exception as e:
                logging.error(f"Error receiving TCP data: {e}")
                return None
        
        return ''.join(buffer) if buffer else None
    
    def close(self) -> None:
        """Close TCP connection."""
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            logging.info("TCP connection closed")


class UDPClient:
    def __init__(self, ip, port, timeout=5):
        self.ip = ip
        self.port = port
        self.client_socket = None
        self.timeout = timeout  

    def connect(self) -> bool:
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.client_socket.bind(("192.168.0.1", self.port))
            self.client_socket.settimeout(self.timeout)  
            self.send_test_message()
            
            print(f"Dinleniyor: {"192.168.0.1"}:{self.port}")

           
            logging.info(f"UDP listening on {self.ip}:{self.port} )")
            return True
           # self.send_test_message()
        except Exception as e:
            logging.error(f"Failed to create UDP socket: {e}")
            self.client_socket = None
            return False
    
    def send_test_message(self):
        try:
            #message = "\n"
            self.client_socket.sendto("PING".encode('ascii'), (self.ip, self.port))
            print(f"PING")
        except Exception as e:
            logging.error(f"Failed to send messa")
            print("Failed to send messa", {e})

    def receive_data(self, timeout=1) -> Optional[str]:
        buffer = []
        last_received_time = time.time()
        if not self.client_socket:
            raise RuntimeError("Call connect() first. I am not connected to UDP")
        
        while True:
            try:
                data, addr = self.client_socket.recvfrom(4096)
                msg = data.decode('ascii', errors='replace')
                buffer.append(msg)
                logging.info(f"Received <- {addr} : {msg}")
                last_received_time = time.time()
            except socket.timeout:
                if time.time() - last_received_time >= timeout:
                    break
            
        
        return ''.join(buffer) if buffer else None

    def close(self) -> None:
        if self.client_socket:
            self.client_socket.close()
            logging.info("UDP socket closed.")
