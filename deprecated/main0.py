from email.utils import formatdate
from datetime import datetime, timezone
import requests
import json
from pprint import pprint
from time import sleep

url: str = "https://api.v2.sondehub.org/sondes/telemetry"
current_datetime: str = formatdate(timeval = None, usegmt=True)

iso_now: str = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

headers: dict[str, str] = {
    "accept" : "text/plain",
    "Date" : current_datetime,
    "User-Agent" : "autorx-1.4.1-beta5",
    "Content-Type" : "application/json",
}
    
body: [dict[str, any]] = [{
    #"dev" : "icss",
        #'...'
        #if all checks pass, adding the dev flag will prevent payload from
        #   being uploaded to the database, even f it is the emtpy string
    "software_name" : "stratus",                    #'...'
    "software_version" : "1.0",                     #'...'
    "uploader_callsign" : "stratus_callsign",       #'...'
    "time_received" : current_datetime,
        #e.g. "2026-01-15T18:50:20.407Z"
        #allows current_datetime
    "manufacturer" : "Vaisala",                     #e.g.
    "type"         : "RS92",                        #e.g. "RS41"
    "serial"       : "M4530852",                    #... "A4530852"
        #serial number if the specific radiosonde
        #needs to be of a specific format, depending on the subtype
        #see https://github-wiki-see.page/m/projecthorus/sondehub-infra/wiki/Radiosonde-Serial-Numbers
        
    "frame"        : 1,                             #e.g. 0
    "datetime" : iso_now,
        #e.g. "2026-01-15T18:50:20.407Z"
        #e.g.fm "2026-01-20T18:50:20.407Z"
        #current_datetime complains saying it cant parse time
    "lat" : 51.4988,
        #e.g. 0 although server complains
    "lon" : -0.1749,
        #e.g. 0 although server complains 
    "alt" : 200,
        #e.g. 0 although server complains
    "subtype" : "RS92-SGP",
        #e.g. "RS41-SG"
        #doesnt seem to care about this value
    "frequency" : 403.0,                                #e.g. 0
    "temp" : 0,                                     #e.g.
    "humidity" : 0,                                 #e.g.
    "vel_h" : 0,                                    #e.g.
    "vel_v" : 0,                                    #e.g.
    "pressure" : 0,                                 #e.g.
    "heading" : 0,                                  #e.g.
    "batt" : 0,                                     #e.g.
    "sats" : 4,
        #number of satellight the sonde sees.
        #e.g. 0.
        #The server complains for any sats < 4 and discards the position as bad.
        #The server accepts sats >= 4 
    "xdata" : "somewhere",                          #'...'
    "snr" : 0,                                      #e.g.
    "rssi" : 0,                                     #e.g.
    "uploader_position" : [                         #e.g.
        0,
        0,
        0
    ],
    "uploader_antenna" : "????",                    #...
    "comment" : "THIS IS A COMMENT"
}]

def main():
    response: requests.Response = requests.put(url, json=body, headers=headers)
    print("Status: ", response.status_code)        #'...'
        #if all checks pass, adding the dev flag will prevent payload from
        #   being uploaded to the database, even f it is the emtpy string                 #'...'

    print("Reason: ", response.reason)
    print("Url: ", response.url)
    print("Ok: ", response.ok)
    print("Header: ", json.dumps(dict(response.headers), indent=2, sort_keys=False))
    print("Encoding: ", response.encoding)
    try:
        print("Body: ", json.dumps(response.json(), indent=2, sort_keys=False))
    except Exception:
        print("Body: ", response.text) #body as decoded string


while True:
    main()
    #break
    sleep(1)
