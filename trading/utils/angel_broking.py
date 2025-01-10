import http.client
import json
from .system_info import get_system_info

class AngelBrokingAPI:
    def __init__(self, access_token, api_key):
        self.access_token = access_token
        self.api_key = api_key
        self.client_local_ip, self.mac_address = get_system_info()
        self.base_url = "apiconnect.angelone.in"

    def _get_headers(self):
        """Generate common headers for API requests"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': self.client_local_ip,
            'X-ClientPublicIP': self.client_local_ip,
            'X-MACAddress': self.mac_address,
            'X-PrivateKey': self.api_key
        }

    def fetch_ohlc(self, symbol_token):
        """Fetch OHLC data for given symbol token"""
        try:
            conn = http.client.HTTPSConnection(self.base_url)
            
            payload = json.dumps({
                "mode": "OHLC",
                "exchangeTokens": {
                    "NSE": [str(symbol_token)]
                }
            })
            
            conn.request("POST", 
                        "/rest/secure/angelbroking/market/v1/quote/", 
                        payload, 
                        self._get_headers())
            
            res = conn.getresponse()
            data = res.read()
            return json.loads(data.decode("utf-8"))
            
        except Exception as e:
            print(f"Error fetching OHLC data: {str(e)}")
            return None