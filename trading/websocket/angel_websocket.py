import websocket
import json
import threading
import time
import struct
from ..logging_config import setup_logger

logger = setup_logger('trading.websocket')

class AngelOneWebSocket:
    def __init__(self, client_id):
        from users.models import User
        
        try:
            user = User.objects.get(client_id=client_id)
            self.client_code = user.client_id
            self.feed_token = user.feed_token
            self.api_key = user.api_key
            self.ws = None
            self.connected = False
            
            logger.info(f"Client Code: {self.client_code}")
            logger.info(f"API Key: {self.api_key}")
            logger.info(f"Feed Token length: {len(self.feed_token) if self.feed_token else 'None'}")
            
            # Add headers for WebSocket authentication
            self.headers = [
                f'Authorization: Bearer {self.feed_token}',
                f'X-API-Key: {self.api_key}',
                f'X-Client-Code: {self.client_code}',
            ]
            
            # WebSocket URL with query parameters
            self.ws_url = (
                f"wss://smartapisocket.angelone.in/smart-stream?"
                f"clientCode={self.client_code}&"
                f"feedToken={self.feed_token}&"
                f"apiKey={self.api_key}"
            )
            
            logger.info(f"WebSocket URL: {self.ws_url}")
            
        except Exception as e:
            logger.error(f"Error initializing WebSocket: {str(e)}")
            raise

    def parse_binary_message(self, binary_data):
        try:
            if isinstance(binary_data, str):
                return None

            # First byte is mode
            mode = binary_data[0]
            
            # Second byte is exchange type
            exchange_type = binary_data[1]

            # Token is next 25 bytes as string (null terminated)
            token_bytes = binary_data[2:27]
            token = token_bytes.split(b'\x00')[0].decode('utf-8')

            # Sequence number at offset 27 (8 bytes)
            sequence = struct.unpack('<Q', binary_data[27:35])[0]

            # Exchange timestamp at offset 35 (8 bytes)
            timestamp = struct.unpack('<Q', binary_data[35:43])[0]

            # LTP at offset 43 (4 bytes) - divided by 100 for actual price
            ltp = struct.unpack('<i', binary_data[43:47])[0] / 100.0

            if len(binary_data) >= 123:  # Make sure we have complete OHLC data
                # Last traded quantity at offset 51 (8 bytes)
                ltq = struct.unpack('<Q', binary_data[51:59])[0]
                
                # Average traded price at offset 59 (8 bytes)
                atp = struct.unpack('<Q', binary_data[59:67])[0] / 100.0
                
                # Volume at offset 67 (8 bytes)
                volume = struct.unpack('<Q', binary_data[67:75])[0]
                
                # Total buy quantity at offset 75 (8 bytes)
                total_buy = struct.unpack('<d', binary_data[75:83])[0]
                
                # Total sell quantity at offset 83 (8 bytes)
                total_sell = struct.unpack('<d', binary_data[83:91])[0]
                
                # Open price at offset 91 (4 bytes)
                open_price = struct.unpack('<i', binary_data[91:95])[0] / 100.0
                
                # High price at offset 99 (4 bytes)
                high = struct.unpack('<i', binary_data[99:103])[0] / 100.0
                
                # Low price at offset 107 (4 bytes)
                low = struct.unpack('<i', binary_data[107:111])[0] / 100.0
                
                # Close price at offset 115 (4 bytes)
                close = struct.unpack('<i', binary_data[115:119])[0] / 100.0

                data = {
                    'mode': mode,
                    'exchange_type': exchange_type,
                    'token': token,
                    'sequence': sequence,
                    'timestamp': timestamp,
                    'ltp': ltp,
                    'ltq': ltq,
                    'atp': atp,
                    'volume': volume,
                    'total_buy_qty': total_buy,
                    'total_sell_qty': total_sell,
                    'open': open_price if open_price > 0 else ltp,
                    'high': high if high > 0 else ltp,
                    'low': low if low > 0 else ltp,
                    'close': close if close > 0 else ltp
                }

                # Calculate percentage change
                prev_close = data['close']
                if prev_close > 0:
                    data['change_percent'] = ((ltp - prev_close) / prev_close) * 100
                else:
                    data['change_percent'] = 0

            else:
                data = {
                    'mode': mode,
                    'exchange_type': exchange_type,
                    'token': token,
                    'sequence': sequence,
                    'timestamp': timestamp,
                    'ltp': ltp,
                    'change_percent': 0
                }

            return data

        except Exception as e:
            logger.error(f"Error parsing binary message: {str(e)}")
            logger.error(f"Binary data: {binary_data.hex() if binary_data else None}")
            return None

    def on_message(self, ws, message):
        try:
            if isinstance(message, str):
                if message == 'pong':
                    logger.debug("Received heartbeat pong")
                return

            parsed_data = self.parse_binary_message(message)
            if parsed_data:
                formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                    time.localtime(parsed_data.get('timestamp')/1000))
                
                logger.info(
                    "\nCRUDEOIL Market Data:"
                    f"\nTime: {formatted_time}"
                    f"\nToken: {parsed_data.get('token')}"
                    f"\nLTP: {parsed_data.get('ltp', 0):.2f}"
                    f"\nChange: {parsed_data.get('change_percent', 0):.2f}%"
                    f"\nVolume: {parsed_data.get('volume', 0):,}"
                    f"\n--- OHLC ---"
                    f"\nOpen: {parsed_data.get('open', 0):.2f}"
                    f"\nHigh: {parsed_data.get('high', 0):.2f}"
                    f"\nLow: {parsed_data.get('low', 0):.2f}"
                    f"\nClose: {parsed_data.get('close', 0):.2f}"
                    f"\n--- Trading Info ---"
                    f"\nLast Traded Qty: {parsed_data.get('ltq', 0):,}"
                    f"\nAvg Traded Price: {parsed_data.get('atp', 0):.2f}"
                    f"\n--- Market Depth ---"
                    f"\nTotal Buy Qty: {parsed_data.get('total_buy_qty', 0):,.0f}"
                    f"\nTotal Sell Qty: {parsed_data.get('total_sell_qty', 0):,.0f}"
                )

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    def on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logger.info(f"WebSocket connection closed. Status code: {close_status_code}")
        self.connected = False

    def on_open(self, ws):
        logger.info("WebSocket connection opened")
        self.connected = True
        self.subscribe_crude_oil()
        self.start_heartbeat()

    def connect(self):
        try:
            websocket.enableTrace(True)
            
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                header=self.headers,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
            logger.info("WebSocket connection initiated")
            
        except Exception as e:
            logger.error(f"Error connecting to WebSocket: {str(e)}")
            raise

    def subscribe_crude_oil(self):
        try:
            if not self.connected:
                logger.error("Cannot subscribe - WebSocket not connected")
                return

            subscription_message = {
                "correlationID": "crude_oil_1",
                "action": 1,  # 1 for subscribe
                "params": {
                    "mode": 2,  # 2 for Quote (OHLC, LTP)
                    "tokenList": [
                        {
                            "exchangeType": 5,  # MCX
                            "tokens": ["432293"]  # CRUDEOIL21OCT24FUT token
                        }
                    ]
                }
            }
            
            self.ws.send(json.dumps(subscription_message))
            logger.info("Subscribed to CRUDEOIL data")
            
        except Exception as e:
            logger.error(f"Error subscribing to CRUDEOIL: {str(e)}")

    def start_heartbeat(self):
        def heartbeat():
            while self.connected:
                try:
                    if self.ws and self.ws.sock and self.ws.sock.connected:
                        self.ws.send("ping")
                        logger.debug("Heartbeat sent")
                        time.sleep(28)
                except Exception as e:
                    logger.error(f"Heartbeat error: {str(e)}")
                    break

        heartbeat_thread = threading.Thread(target=heartbeat)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()