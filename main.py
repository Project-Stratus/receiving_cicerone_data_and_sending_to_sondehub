import paho.mqtt.client as mqtt
import json
import base64
from telemetry import telemetry_t
import telemetry
import sondehub
import logger
import time
# TTN details
app_id = "test-stratus"
access_key = "NNSXS.G4Q4JAWU7T26BNCY54K34AFKIWBDCXJPUOIZHKY.CQYRXMARINPZDH4RVM2LN5T7I57BXO6JEMJ6XTHQTIBSSSAOID7A"
region = "eu1"  # e.g. eu1, nam1, au1 etc.

# MQTT endpoint for TTN
broker = f"{region}.cloud.thethings.network"
port = 8883

# Topics
uplink_topic = f"v3/{app_id}@ttn/devices/+/up"

# Called when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to TTN MQTT")
        client.subscribe(uplink_topic)
        print(f"Subscribed to {uplink_topic}")
    else:
        print(f"Failed to connect, return code {rc}")

body: dict[str, any] = sondehub.create_body()
headers: dict[str, str] = sondehub.create_headers()

# Called when a message is received
def on_message(client, userdata, msg):
    telem: telemetry_t = telemetry_t()
    telem.time_received = sondehub.get_current_utc_iso_datetime()
    payload = json.loads(msg.payload.decode())
    logger.info_print(f"payload: {payload}")
    frm_payload = payload["uplink_message"]["frm_payload"]
    logger.info_print(f"frm_payload: {frm_payload}")
    struct_binary: bytes = base64.b64decode(frm_payload)
    logger.info_print(f"struct binary: {struct_binary}")
    telemetry.decode_packet(telem, struct_binary)
    logger.info_print(f"Telemetry: {telem}")
    sondehub.send_telemetry(telem, headers, body)
    
TEST_BINARY_DATA: bytes = b'\xc7\xa5\xb2\x1e@\x9a\xe5\xff{\xf6\x00\x00\x01\x00\x00\x00\x00\xe0\x00\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x15\xec\x00\x08'

def main():
    # Create and configure client
    client = mqtt.Client()
    client.username_pw_set(app_id, access_key)
    client.tls_set()  # TTN requires TLS

    client.on_connect = on_connect
    client.on_message = on_message

    # Connect and loop
    client.connect(broker, port)
    client.loop_forever()

def test_main():
    class fake_payload_t:
        def __init__(self):
            pass
        def decode(self) -> str:
            return json.dumps({
                "uplink_message" : {
                    "frm_payload" : base64.b64encode(TEST_BINARY_DATA).decode()}})
    class fake_msg_t:
        def __init__(self):
            self.payload = fake_payload_t()
    class fake_client_t:
        def __init__(self):
            pass
        def subscribe(self, uplink_topic: str) -> None:
            print(f"PRETENDING TO SUBSCRIBE to {uplink_topic}")
    test_client = fake_client_t()
    test_user_data = None
    test_flags = None
    test_rc: int = 0
    on_connect(test_client, test_user_data, test_flags, test_rc)
    while (True):
        test_message = fake_msg_t()
        on_message(test_client, test_user_data, test_message)
        time.sleep(1)

if __name__ == "__main__":
    main()

