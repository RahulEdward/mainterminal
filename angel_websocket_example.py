import threading
import websocket
import time
import signal
import sys
import json
import http.client
from smartWebSocketV2 import SmartWebSocketV2  # Import your local class

# Define your credentials
client_id = "LLVR1277"
client_pin = "2105"
totp_code = "090208"
api_key = "z6DaAedv"
client_local_ip = "CLIENT_LOCAL_IP"
client_public_ip = "CLIENT_PUBLIC_IP"
mac_address = "MAC_ADDRESS"
state_var = "STATE_VARIABLE"

# Global variables for tokens
AUTH_TOKEN = None
FEED_TOKEN = None
ws = None

# Generate Access Token and Feed Token
def generate_tokens():
    global AUTH_TOKEN, FEED_TOKEN
    conn = http.client.HTTPSConnection("apiconnect.angelone.in")

    # Prepare login payload
    payload = json.dumps({
        "clientcode": client_id,
        "password": client_pin,
        "totp": totp_code,
        "state": state_var
    })

    # Headers for login request
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-UserType': 'USER',
        'X-SourceID': 'WEB',
        'X-ClientLocalIP': client_local_ip,
        'X-ClientPublicIP': client_public_ip,
        'X-MACAddress': mac_address,
        'X-PrivateKey': api_key
    }

    # Send request
    conn.request("POST", "/rest/auth/angelbroking/user/v1/loginByPassword", payload, headers)
    res = conn.getresponse()
    data = res.read()
    response = json.loads(data.decode("utf-8"))

    # Extract tokens
    AUTH_TOKEN = response['data']['jwtToken']
    FEED_TOKEN = response['data']['feedToken']
    conn.close()

    print(f"AUTH_TOKEN: {AUTH_TOKEN}")
    print(f"FEED_TOKEN: {FEED_TOKEN}")

# WebSocket Event Handlers
def on_data(wsapp, message):
    # Initialize SmartWebSocketV2 with tokens
    ws_parser = SmartWebSocketV2(AUTH_TOKEN, api_key, client_id, FEED_TOKEN)

    # Parse the binary message using the SmartWebSocketV2 method
    if isinstance(message, bytes):
        parsed_message = ws_parser._parse_binary_data(message)  # Reusing the method
        if parsed_message:
            # Divide the open, high, low, close, and ltp by 100
            parsed_message['last_traded_price'] = parsed_message['last_traded_price'] / 100
            parsed_message['open_price_of_the_day'] = parsed_message.get('open_price_of_the_day', 0) / 100
            parsed_message['high_price_of_the_day'] = parsed_message.get('high_price_of_the_day', 0) / 100
            parsed_message['low_price_of_the_day'] = parsed_message.get('low_price_of_the_day', 0) / 100
            parsed_message['closed_price'] = parsed_message.get('closed_price', 0) / 100

            # Print the parsed data
            print(f"Token: {parsed_message['token']}")
            print(f"LTP: {parsed_message['last_traded_price']}")
            print(f"Open: {parsed_message['open_price_of_the_day']}")
            print(f"High: {parsed_message['high_price_of_the_day']}")
            print(f"Low: {parsed_message['low_price_of_the_day']}")
            print(f"Close: {parsed_message['closed_price']}")
            print("-" * 40)

def on_open(wsapp):
    print("WebSocket opened")
    subscribe_to_quotes()

def on_error(wsapp, error):
    print(f"WebSocket error: {error}")

def on_close(wsapp):
    print("WebSocket closed")

# Function to Subscribe to Quotes
def subscribe_to_quotes():
    if AUTH_TOKEN and FEED_TOKEN:
        # Create a subscription message
        subscribe_message = json.dumps({
            "correlationID": "ws_test",
            "action": 1,  # 1 for subscribe
            "params": {
                "mode": 2,  # Fetch quotes
                "tokenList": [{"exchangeType": 5, "tokens": ["432293"]}]  # CRUDEOIL21OCT24FUT token
            }
        })
        ws.send(subscribe_message)
        print("Subscribed to CRUDEOIL21OCT24FUT quotes")

# WebSocket Connection Function
def connect_websocket():
    global ws
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "x-api-key": api_key,
        "x-client-code": client_id,
        "x-feed-token": FEED_TOKEN
    }

    ws = websocket.WebSocketApp("wss://smartapisocket.angelone.in/smart-stream",
                                header=headers,
                                on_open=on_open,
                                on_message=on_data,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()

# Function to Close the WebSocket Connection Gracefully
def close_connection():
    if ws:
        ws.close()

# Function to Handle Keyboard Interrupt (CTRL+C)
def signal_handler(sig, frame):
    print('Interrupt received, closing connection...')
    close_connection()
    sys.exit(0)

# Main Program Execution
if __name__ == "__main__":
    # Generate tokens for WebSocket connection
    generate_tokens()

    # Connect to WebSocket and use the parser from SmartWebSocketV2
    threading.Thread(target=connect_websocket).start()

    # Handle CTRL+C gracefully
    signal.signal(signal.SIGINT, signal_handler)

    # Keep the main thread alive to capture KeyboardInterrupt
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down WebSocket connection...")
        close_connection()
