import struct
import logger

class telemetry_t:
    '''see https://github-wiki-see.page/m/projecthorus/sondehub-infra/wiki/SondeHub-Telemetry-Format'''
    def __init__(self):
        self.latitude: float = 0.0      #Latitude (decimal degrees)
        self.longitude: float = 0.0     #Longitude (decimal degrees)
        self.altitude: float = 0.0      #Altitude (metres)
        self.temperature: float = 0.0   #Measured Temperature (deg C)
        self.pressure: float = 0.0      #Measured Pressure (hPa)
        self.illuminance: float = 0.0   #ignored
        self.humidity: float = 0.0      #Measured Relative Humidity (%)
        self.siv: float = 0.0           #Number of SVs used in position solution    
        self.time_received: str = ""    #The time the telemetry packet was received. UTC time in YYYY-MM-DDTHH:MM:SS.SSSSSSZ format.
        self.frame: int = 0             #Frame Number, ideally unique over the entire flight.
    def __str__(self):
        s: str = "{"
        s += f"\n\tlattitude     = {self.latitude}"
        s += f"\n\tlongitude     = {self.longitude}"
        s += f"\n\taltitude      = {self.altitude}"
        s += f"\n\ttemperature   = {self.temperature}"
        s += f"\n\tpressure      = {self.pressure}"
        s += f"\n\tilluminance   = {self.illuminance}"
        s += f"\n\thumidity      = {self.humidity}"
        s += f"\n\tsiv           = {self.siv}"
        s += f"\n\ttime_received = {self.time_received}"
        s += f"\n\tframe         = {self.frame}"
        s += "\n}"
        return s

def decode_packet(telemetry: telemetry_t, packet: bytes) -> None:
    """
        receives data that the cicercone sends out binary data in the following form:
            struct GPSData {
              int32_t latitude;
              int32_t longitude;
              int32_t altitude;
              int32_t temp;
              int32_t pressure;
              int32_t illuminance;
              int32_t humidity;
              byte siv;
            };
        decode the packet to a python tuple
    """
    FMT: str = "<8i"
    latitude, longitude, altitude, temp, pressure, illuminance, humidity, siv \
               = struct.unpack(FMT, packet)
    logger.info_print(f"Decoded Packet: {latitude=}, {longitude=}, {altitude=}, {temp=}, {pressure=}, {illuminance=}, {humidity=}, {siv=}")
    """only latitude, longitude, altitude and siv are actually measured"""
    telemetry.latitude = latitude / 1e7
    telemetry.longitude = longitude / 1e7
    telemetry.altitude = altitude
    telemetry.siv = siv
    """temp, pressure, illuminance, humiidity are not measured and left
        uninitialized in the cicerone code (so could be possibly garbage values).
        Hence leave these fields as zero"""
