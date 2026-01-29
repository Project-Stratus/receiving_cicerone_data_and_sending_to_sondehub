from email.utils import formatdate
from datetime import datetime, timezone
import requests
import json
from pprint import pprint
from time import sleep
from telemetry import telemetry_t
import logger

'''
Possible Errors in Telemetry (that sondehub will reject):
- zero longitude or latitude (i.e. null island)
- zero altitude -> altitude cannot be exactly zero
- invalid altitude -> 50000 altitude cap
- < 4 SVs (satellights, sats), including negative values
- Sonde reported time too far from current UTC time. Either sonde time or
    system time is invalid. (Threshold: 48 hours)
- Sonde reported time too far in the future. Either sonde time or system time
    is invalid. (Threshold: 60 seconds)
- "Unable to parse time" (datetime field)
- "Payload ID A4530852 from Sonde type RS92 is invalid."
- "dev" field (not technicall an error, but useful for testing) 
- humidity < 0
- pressure < 0
The following errors are not tested by the server (or this code):
- invalid longitude or latitude (except 0, 0)
- impossibly-low negative altitudes
- impossibly-high SVs
- 
Find out the purpose of each field
- perhaps frame
See if you can add random stuff to the payload
Test if you can add custom fields to sondehub
'''

def fix_errors(telemetry) -> None:
    ALTITUDE_CAP: float = 50000
    MIN_SIV: int = 4
    DEFAULT_ALTITUDE: float = ALTITUDE_CAP - 1
    DEFAULT_SIV: int = 1e6
    DEFAULT_HUMIDITY: float = 1e6
    DEFAULT_PRESSURE: float = 1e6
    if telemetry.latitude == 0 and telemetry.longitude == 0:
        logger.error_print("latitude and longitude are zero. sondehub will reject data. no change will be made however")
    if telemetry.siv < MIN_SIV:
        logger.error_print(f"siv = {telemetry.siv} < 4 (aka 'sats' / 'number of sats used in fix'). sondehub will reject data. changing to {DEFAULT_SIV}") 
    if telemetry.humidity < 0:
        logger.error_print(f"humidity {telemetry.humidity} is negative. sondehub will reject data. changing to {DEFAULT_HUMIDITY}")
    if telemetry.pressure < 0:
        logger.error_print(f"pressure {telemetry.pressure}hPa is negative. sondehub will reject data. changing to {DEFAULT_PRESSURE}")        
    if telemetry.altitude == 0:
        logger.error_print(f"altitude is zero. sondehub will reject data. changing to {DEFAULT_ALTITUDE}")
        telemetry.altitude = DEFAULT_ALTITUDE
    elif telemetry.altitude >= ALTITUDE_CAP:
        logger.error_print(f"altitude {telemetry.altitude}m exceeds {ALTITUDE_CAP}m altitude cap. sondehub will reject data. changing to {DEFAULT_ALTITUDE}")
        telemetry.altitude = DEFAULT_ALTITUDE
    #date is not checked here...
    #we assume the programmer has correctly set telemetry.time_received
    #to a utc iso datetime within [-48hrs, 60s] of the datetime when the message
    #is sent
    #otherwise sondehub will reject data

def get_current_utc_iso_datetime() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

def get_utc_rfc7231_datetime() -> str:
    return formatdate(timeval = None, usegmt=True)

def create_headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    headers["accept"] = "text/plain"
    headers["User-Agent"] = "autorx-1.4.1-beta5" #no clue what this is...
    headers["Content-Type"] = "application/json"
    return headers

def update_headers_datetime(headers: dict[str, str]) -> None:
    headers["Date"] = get_utc_rfc7231_datetime()

def create_body() -> dict[str, any]:
    body: dict[str, any] = {}
    body["software_name"] = "stratus"
    body["software_version"] = "1.0"
    body["uploader_callsign"] = "stratus_callsign"
    body["manufacturer"] = "Vaisala"
    body["type"] = "RS92"
    body["serial"] = "M4530852" 
    body["subtype"] = "RS92-SGP"
    body["uploader_antenna"] = "????"
    body["ref_position"] = "GPS"
    body["ref_datetime"] = "UTC"      #maybe change to GPS if we get time from MCU
    #body["uploader_antenna"] = "???" #Station antenna information, free-text string.
    return body

def update_body(body: dict[str, any], telemetry: telemetry_t) -> None:
    body["time_received"] = telemetry.time_received
    body["frame"] = telemetry.frame
    body["datetime"] = telemetry.time_received #change if we get time from MCU
    body["lat"] = telemetry.latitude
    body["lon"] = telemetry.longitude
    body["alt"] = telemetry.altitude
    body["temp"]= telemetry.temperature
    body["humidity"] = telemetry.humidity
    body["pressure"] = telemetry.pressure      
    body["vel_h"] = 0   #TODO
    body["vel_v"] = 0   #TODO                                      
    body["heading"] = 0 #TODO                 
    body["sats"] = telemetry.siv  #number of satellights/SV seen by GPS, that were used in position solution)
    #body["batt"] = 0   #battery voltage           
    #body["burst_timer"] = 0 #RS41 burst-timer value, in seconds
    #body["xdata"] = ????
        #no clue how this works
        #xdata 0501036302BB18B08100#8002629471A00012FD6C0A66
        #gives interesting response
    #body["frequency"] = 403 #Radiosonde Transmit frequency in MHz, estimated by receiver software)
    #body["tx_frequency"] = telemetry.transmit_frequency #(Radiosonde Transmit frequency in MHz, from radiosonde telemtry)
    #body["snr"] = 0    #Signal-to-Noise ratio of the received signal_               
    #body["rssi"] = 0   #Received-Signal-Strength-Indication of the signal                                 
    #body["uploader_position"] = [0, 0, 0] #station position as [lat, lon, alt]

def str_request(url: str, headers: dict[str, str], body: dict[str, any]) -> str:
    s: str = ""
    s +=   f"url = {url}"
    s += f"\nheaders = {json.dumps(headers, indent=2, sort_keys=False)}"
    s += f"\nbody    = {json.dumps(body, indent=2, sort_keys=False)}"
    return s

def put_onto_sondehub(
    url: str,
    headers: dict[str, str],
    body: dict[str, any]
) -> requests.Response:
    return requests.put(url, json=[body], headers=headers)

def str_response(response: requests.Response) -> str:
    s: str = ""
    s +=   f"status   = {response.status_code}"
    s += f"\nreason   = {response.reason}"
    s += f"\nurl      = {response.url}"
    s += f"\nok       = {response.ok}"
    s += f"\nheaders  = {json.dumps(dict(response.headers), indent=2, sort_keys=False)}"
    s += f"\nencoding = {response.encoding}"
    body: str = ""
    try:
        body = str(json.dumps(response.json(), indent=2, sort_keys=False))
    except Exception:
        body = str(response.text) #body as decoded string
    s += f"\nbody     = {body}"
    return s

def was_telemetry_put_onto_sondhub(response: requests.Response) -> bool:
    OK: int = 200
    return response.status_code == OK and response.ok

def retrieve_error(response: requests.Response) -> tuple[str, dict[str, any]]:
    ERRORS_FIELD: str = "errors"
    ERROR_INDEX: int = 0
    ERROR_MESSAGE_FIELD: str = "error_message"
    PAYLOAD_FIELD: str = "payload"
    errors = response.json().get("ERRORS_FIELD")
    if (error == None):
        raise Exception(f"within requests.json(), there is no such field as '{ERRORS_FIELD}'")
    if (len(errors) > ERROR_INDEX):
        raise Exception(f"within requests.json()[{ERRORS_FIELD}], the error index of '{ERROR_INDEX}' exceeds the number of errors ({len(errors)})")
    error = errors[ERROR_INDEX]
    error_message = error[ERROR_MESSAGE_FIELD]
    payload = error[PAYLOAD]
    if (error_message == None):
        raise Exception(f"within requests.json()[{ERRORS_FIELD}][{ERROR_INDEX}], there is no such field as '{ERROR_MESSAGE_FIELD}'")
    if (payload == None):
        raise Exception(f"within requests.json()[{ERRORS_FIELD}][{ERROR_INDEX}], there is no such field as '{PAYLOAD_FIELD}'")        
    return error_message, payload
    #error: dict[str, str | dict[str, any]] = requests.json()["errors"][0]
    #return error["error_message"], error["payload"]
    #may throw an exception if response does not conform to expected format

def output_sent_and_recieved_payload_differences(
    body: dict[str, any],
    payload: dict[str, any]
) -> None:
    for field in body:
        if field not in payload:
            logger.error_print(f"received payload does not have field {field}")
        elif body[field] != payload[field]:
            logger.error_print(f"field {field} does not match in body ({body[field]}) and payload ({payload[field]})")

def send_telemetry(
    telemetry: telemetry_t,
    headers: dict[str, str],
    body: dict[str, any]
) -> bool:
    URL: str = "https://api.v2.sondehub.org/sondes/telemetry"
    fix_errors(telemetry)
    logger.info_print(f"Modified Telemetry: {telemetry}")
    update_headers_datetime(headers)
    update_body(body, telemetry)
    logger.info_print(str_request(URL, headers, body))
    response: requests.Response = put_onto_sondehub(URL, headers, body)
    logger.info_print(str_response(response))
    if (was_telemetry_put_onto_sondhub(response)):
        logger.event_print("telemetry put onto sondehub successfully")
        return True
    logger.error_print("failed to put telemetry onto sondehub")
    try:
        logger.error_message, payload = retrieve_error(response)
    except Exception as e:
        logger.error_print(f"Cannot Retrive Error From Response: {e}")
        return False
    logger.error_print(f"{error_message}")
    output_sent_and_recieved_payload_differences(body, payload)
    return False

def main() -> None:
    telemetry: telemetry_t = telemetry_t()
    telemetry.latitude = 51.4988
    telemetry.longitude = -0.1749
    telemetry.altitude = 200.0
    telemetry.temperature = 20.0
    telemetry.pressure = 1000
    telemetry.illuminance = 0.2
    telemetry.humidity = 75
    telemetry.siv = 4
    telemetry.time_received = get_current_utc_iso_datetime()
    telemetry.frame = 1
    headers: dict[str, str] = create_headers()
    body: dict[str, any] = create_body()
    def once():
        nonlocal telemetry, headers, body
        send_telemetry(telemetry, headers, body)
    def loop():
        nonlocal telemetry, headers, body
        while True:
            once()
            telemetry.latitude += 0.01
            telemetry.longitude += 0.01
            sleep(1)
    loop()

if __name__ == "__main__":
    main()

