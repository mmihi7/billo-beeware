import asyncio
import json
import logging
from typing import Callable, Optional, Dict, Any

class WebSocketService:
    def __init__(self):
        self.connection = None
        self.connected = False
        self.subscribers = set()
        self.logger = logging.getLogger(__name__)
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 1  # Start with 1 second delay
        self._reconnect_task = None
        self._message_handlers = {}
    
    async def connect(self, url: str):
        """Connect to the WebSocket server"""
        if self.connected:
            return True
            
        try:
            import websockets
            self.connection = await websockets.connect(url)
            self.connected = True
            self._reconnect_attempts = 0
            self._start_message_loop()
            self.logger.info("WebSocket connected")
            return True
        except Exception as e:
            self.logger.error(f"WebSocket connection failed: {e}")
            await self._handle_reconnect(url)
            return False
    
    def _start_message_loop(self):
        """Start the message receiving loop"""
        asyncio.create_task(self._message_loop())
    
    async def _message_loop(self):
        """Continuously receive and process messages"""
        while self.connected and self.connection:
            try:
                message = await self.connection.recv()
                data = json.loads(message)
                self._handle_message(data)
            except Exception as e:
                self.logger.error(f"Error in message loop: {e}")
                self.connected = False
                break
    
    def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        message_type = data.get('type')
        if message_type in self._message_handlers:
            for handler in self._message_handlers[message_type]:
                try:
                    handler(data)
                except Exception as e:
                    self.logger.error(f"Error in message handler: {e}")
    
    async def _handle_reconnect(self, url: str):
        """Handle reconnection logic"""
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            self.logger.error("Max reconnection attempts reached")
            return
            
        self._reconnect_attempts += 1
        delay = min(self._reconnect_delay * (2 ** (self._reconnect_attempts - 1)), 30)
        self.logger.info(f"Reconnecting in {delay} seconds... (attempt {self._reconnect_attempts}/{self._max_reconnect_attempts})")
        
        await asyncio.sleep(delay)
        await self.connect(url)
    
    def subscribe(self, message_type: str, callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to a specific message type"""
        if message_type not in self._message_handlers:
            self._message_handlers[message_type] = set()
        self._message_handlers[message_type].add(callback)
    
    def unsubscribe(self, message_type: str, callback: Callable[[Dict[str, Any]], None]):
        """Unsubscribe from a specific message type"""
        if message_type in self._message_handlers and callback in self._message_handlers[message_type]:
            self._message_handlers[message_type].remove(callback)
    
    async def send(self, message: Dict[str, Any]):
        """Send a message through the WebSocket"""
        if not self.connected or not self.connection:
            self.logger.warning("Cannot send message: WebSocket not connected")
            return False
            
        try:
            await self.connection.send(json.dumps(message))
            return True
        except Exception as e:
            self.logger.error(f"Failed to send WebSocket message: {e}")
            self.connected = False
            return False
    
    async def close(self):
        """Close the WebSocket connection"""
        self.connected = False
        if self.connection:
            await self.connection.close()
            self.connection = None

# Singleton instance
websocket_service: Optional[WebSocketService] = None

def get_websocket_service() -> WebSocketService:
    """Get the WebSocket service instance"""
    global websocket_service
    if websocket_service is None:
        websocket_service = WebSocketService()
    return websocket_service
