from .angel_websocket import AngelOneWebSocket
from ..logging_config import setup_logger

logger = setup_logger('trading.market_data')

class MarketDataManager:
    def __init__(self, client_id):
        self.client_id = client_id
        self.websocket = None

    def start(self):
        """Start WebSocket connection"""
        try:
            self.websocket = AngelOneWebSocket(self.client_id)
            self.websocket.connect()
            logger.info(f"Market data manager started for client {self.client_id}")
        except Exception as e:
            logger.error(f"Error starting market data manager: {str(e)}")
            raise