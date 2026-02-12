import asyncio
from typing import Optional
from .config import config

class AsyncMotor:
    """
    Async communicator for Applied Motion drive using eSCL TCP protocol.
    """

    def __init__(self, name, ip, port=7776, timeout=None):
        self.name = name
        self.ip = ip
        self.port = port
        self.timeout = timeout or config.motion.socket_timeout
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

    async def __aenter__(self):
        """Connects to the motor asynchronously."""
        try:
            future = asyncio.open_connection(self.ip, self.port)
            self.reader, self.writer = await asyncio.wait_for(future, timeout=self.timeout)
            return self
        except (asyncio.TimeoutError, ConnectionRefusedError) as e:
            self._log_error(f"Connection failed: {e}")
            raise e

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the connection."""
        if self.writer:
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except Exception:
                pass

    def _build_packet(self, command: str) -> bytes:
        """Builds a complete SCL packet."""
        header = config.protocol.header_bytes
        terminator = config.protocol.terminator_byte
        encoding = config.protocol.encoding
        packet = command.encode(encoding)
        return header + packet + terminator

    def _parse_response(self, data: bytes) -> Optional[str]:
        """Extracts and decodes the payload."""
        if not data:
            return None
        header = config.protocol.header_bytes
        terminator = config.protocol.terminator_byte
        encoding = config.protocol.encoding
        
        if len(data) < len(header) + len(terminator):
            return None

        payload = data[len(header):-len(terminator)]
        return payload.decode(encoding).strip()

    def _log_info(self, message: str):
        print(f"[{self.name}@{self.ip}] {message}")

    def _log_error(self, message: str):
        print(f"[{self.name}@{self.ip}] !!! {message}")

    async def send_command(self, command: str) -> Optional[str]:
        """
        Sends a command asynchronously and returns the response.
        Returns None on failure.
        """
        if not command:
            return None

        try:
            full_packet = self._build_packet(command)
            
            if not self.writer:
                raise ConnectionError("Not connected")

            self.writer.write(full_packet)
            await self.writer.drain()

            data = await asyncio.wait_for(
                self.reader.read(config.motion.recv_buffer_size), 
                timeout=self.timeout
            )
            
            response = self._parse_response(data)
            
            if response is None:
                self._log_error(f"No response for '{command}'")
                return None

            self._log_info(f"Sent '{command}' -> Received: '{response}'")
            return response

        except asyncio.TimeoutError:
            self._log_error(f"Timeout for '{command}'")
            return None
        except Exception as e:
            self._log_error(f"Exception sending '{command}': {e}")
            return None
