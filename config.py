KEY = 'change-me'
THINGSPEAK_URL = 'https://api.thingspeak.com/update?api_key=%s&field1=' % KEY
CONFIG = {
    'debug': True,
    'thingspeak_url': THINGSPEAK_URL,
    'wifi': {
        'essid': 'network_name',
        'password': 'pass',
        'status': {
            False: 250,
            True: 1000
        }
    },
    'sleep': {
        'connected': 30000,
        'not_connected': 3000
    }
}
