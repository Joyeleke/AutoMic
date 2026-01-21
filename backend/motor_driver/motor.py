"""
SCL Motor communication module.
"""

import socket
from typing import Optional
from .config import config

class Motor:
    """
    Communicates with an Applied Motion drive using the eSCL TCP protocol.
    This class handles only the low-level communication with a single motor.
    """

    def __init__(self, name, ip, port=7776, timeout=None):
        self.name = name
        self.drive_address = (ip, port)
        self.timeout = timeout or config.motion.socket_timeout
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self):
        """Connects the socket for communication."""
        self.socket.settimeout(self.timeout)
        self.socket.connect(self.drive_address)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the socket."""
        self.socket.close()

    def _build_packet(self, command: str) -> bytes:
        """Builds a complete SCL packet with protocol headers and terminator."""
        header = config.protocol.header_bytes
        terminator = config.protocol.terminator_byte
        encoding = config.protocol.encoding
        packet = command.encode(encoding)
        return header + packet + terminator

    def _parse_response(self, data: bytes) -> Optional[str]:
        """Extracts and decodes the payload from a response packet."""
        if not data:
            return None

        header = config.protocol.header_bytes
        terminator = config.protocol.terminator_byte
        encoding = config.protocol.encoding
        payload = data[len(header):-len(terminator)]
        return payload.decode(encoding).strip()

    def _log_info(self, message: str):
        """Log informational message."""
        print(f"[{self.name}@{self.drive_address[0]}] {message}")

    def _log_error(self, message: str):
        """Log error message."""
        print(f"[{self.name}@{self.drive_address[0]}] !!! {message}")

    
    def send_command(self, command: str) -> bool:
        """
        Sends a single SCL command and returns the response.
        """

        if not command:
            self._log_error("Empty command provided")
            return False
        
        try:
            full_packet = self._build_packet(command)
            self.socket.sendall(full_packet)
        
            data = self.socket.recv(config.motion.recv_buffer_size)
            response = self._parse_response(data)
        
            if response is None:
                self._log_error(f"No response for command '{command}'")
                return False

            self._log_info(f"Sent '{command}' -> Received: '{response}'")
            return True 

        except socket.timeout:
            self._log_error(f"Timeout for command '{command}'")
            return False
        except Exception as e:
            self._log_error(f"Exception: {e}")
            return False
