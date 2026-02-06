This project is to be run on a PC with access to the internet

The program developed will indefinitely
- wait until it receives a message (containing encoded telemetry) that is sent by the cicerone (a MCU found on the balloon)
- decode this message to telemetry data (that can be manipulated with the standard python datatypes)
- put the telemetry data (altitude, longitude, latitude, sivs etc.) onto [sondehub](https://sondehub.org/#!mt=Mapnik&mz=15&qm=3h&mc=51.50176,-0.17248&box=aboutbox), such that the balloon can be seen on their website. 

To Run This Code:
-  clone this repository
```
git clone https://github.com/Project-Stratus/receiving_cicerone_data_and_sending_to_sondehub.git
```
-  re-define the values for the following global variables found in main.py:
    - `app_id = "test-stratus"`
    - `access_key = "NNSXS.G4Q4JAWU7T26BNCY54K34AFKIWBDCXJPUOIZHKY.CQYRXMARINPZDH4RVM2LN5T7I57BXO6JEMJ6XTHQTIBSSSAOID7A"`
- its highly unlikely these global variables in `main.py` will need to be redefined?
    -  `region = "eu1"  # e.g. eu1, nam1, au1 etc.`
    - `port = 8883`
-  run main.py
