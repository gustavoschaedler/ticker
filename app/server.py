from datetime import datetime
import websockets
import asyncio
import json
import os
import logging
import signal
from typing import List, Optional
from websockets import ClientProtocol

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

AUTHORIZED_TOKEN: Optional[str] = os.getenv("TOKEN", None)
TICKER: Optional[str] = os.getenv("TICKER", None)

if not TICKER:
    raise ValueError(
        "TICKER environment variable must be set. Example: btcusdt@ticker")
if not AUTHORIZED_TOKEN:
    raise ValueError("TOKEN environment variable must be set")


def format_price(price: str, format_value: str = "{:.0f}") -> str:
    """
    Formats a price to the specified format.

    :param price: The price as a string.
    :param format_value: The format string to apply to the price.
    :return: The formatted price.
    """
    return format_value.format(float(price))


def format_datetime(timestamp: int, dt_format: str = '%d.%m.%Y %H:%M:%S') -> str:
    """
    Converts a timestamp to a formatted datetime string.

    :param timestamp: The timestamp in milliseconds.
    :param dt_format: The datetime format string.
    :return: The formatted datetime string.
    """
    return datetime.fromtimestamp(timestamp / 1000).strftime(dt_format)


class BinanceClient:
    """
    Class for connecting to and receiving data from Binance WebSocket.

    Attributes:
        ticker (str): The ticker symbol for the WebSocket stream.
        url (str): The URL of the WebSocket stream.
    """

    def __init__(self, ticker: str) -> None:
        self.ticker = ticker
        self.url = f"wss://fstream.binance.com/stream?streams={ticker}"
        self.websocket = None

    async def __aenter__(self):
        """
        Async context manager entry point.
        """
        self.websocket = await websockets.connect(
            self.url,
            ping_timeout=None,
            max_size=10000000
        )
        return self.websocket

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit point.
        """
        if self.websocket:
            await self.websocket.close()

    async def subscribe(self):
        """
        Connects to the Binance WebSocket.
        """
        return self

    @staticmethod
    def format_data(data: dict) -> dict:
        """
        Formats the raw data received from Binance into a structured dictionary.

        :param data: The raw data from Binance.
        :return: A dictionary with the formatted data.
        """
        return {
            "event_time": format_datetime(data['E']),
            "type_event": data['e'],
            "high_price": format_price(data['h']),
            "last_price": format_price(data['c']),
            "low_price": format_price(data['l']),
            "open_price": format_price(data['o']),
            "price_change": format_price(data['p'], "{:.2f}"),
            "price_change_percent": format_price(data['P'], "{:.4f}"),
            "symbol": data['s'],
            "weighted_avg_price": format_price(data['w'])
        }


class WebSocketServer:
    """
    Class to manage WebSocket connections with clients.

    Attributes:
        host (str): The host address for the server.
        port (int): The port number for the server.
        connected_clients (List[ClientProtocol]): List of currently connected clients.
        active_connections (int): The count of active WebSocket connections.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8765) -> None:
        self.host = host
        self.port = port
        self.connected_clients: List[ClientProtocol] = []
        self.active_connections = 0

    async def authenticate(self, websocket: ClientProtocol) -> bool:
        """
        Authenticates a client by checking the received token.

        :param websocket: The client's WebSocket connection.
        :return: True if authenticated, False otherwise.
        """
        try:
            message = await websocket.recv()
            data = json.loads(message)
            if data.get("token") != AUTHORIZED_TOKEN:
                await websocket.close(reason="Unauthorised")
                logging.info("Connection rejected: Unauthorised token")
                return False
            return True
        except (ValueError, KeyError):
            await websocket.close(reason="Invalid authentication data")
            logging.info("Connection rejected: Invalid authentication data")
            return False

    async def handle_client(self, websocket: ClientProtocol) -> None:
        """
        Manages the connection with a specific client.

        :param websocket: The client's WebSocket connection.
        """
        client_ip = websocket.remote_address[0] if websocket.remote_address else "Unknown"
        logging.info(f"New connection attempt from: {client_ip}")

        # Authentication
        if not await self.authenticate(websocket):
            return

        # Authorised connection
        self.connected_clients.append(websocket)
        self.active_connections += 1
        logging.info(
            f"Authorised connection from {client_ip} | Active connections: {self.active_connections}")

        try:
            binance_client = BinanceClient(TICKER)
            async with await binance_client.subscribe() as binance_ws:
                headers = {
                    "method": "SUBSCRIBE",
                    "params": [TICKER],
                    "id": 1
                }
                await binance_ws.send(json.dumps(headers))

                async for msg in binance_ws:
                    raw_data = json.loads(msg)
                    if 'result' in raw_data:
                        continue

                    data = raw_data['data']
                    formatted_data = binance_client.format_data(data)
                    await websocket.send(json.dumps(formatted_data))
        except websockets.exceptions.ConnectionClosedOK:
            logging.info(f"Client {client_ip} disconnected.")
        except Exception as e:
            logging.error(f"Error handling client {client_ip}: {str(e)}")
        finally:
            self.active_connections -= 1
            if websocket in self.connected_clients:
                self.connected_clients.remove(websocket)
            logging.info(
                f"Connection with {client_ip} closed | Active connections: {self.active_connections}")

    async def shutdown(self) -> None:
        """
        Gracefully shuts down the server by closing all client connections.
        """
        logging.info("Shutting down server...")
        for client in self.connected_clients:
            await client.close()
        logging.info("Server shutdown complete.")

    async def start(self) -> None:
        """
        Starts the WebSocket server and sets up signal handlers for graceful shutdown.
        """
        logging.info(
            f"Server active and waiting for WebSocket connections on ws://{self.host}:{self.port}")
        start_server = await websockets.serve(self.handle_client, self.host, self.port)

        # Set up signals for server shutdown
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig, lambda: asyncio.create_task(self.shutdown()))

        await start_server.wait_closed()


if __name__ == '__main__':
    server = WebSocketServer()
    asyncio.run(server.start())
