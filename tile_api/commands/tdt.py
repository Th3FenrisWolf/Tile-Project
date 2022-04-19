# tile double-tap 
# i.e. button related stuff

from enum import Enum

class Tdt_Cmd_Code(Enum):
    CONFIG      = b"\x01"
    READ_CONFIG = b"\x02"

class Tdt_Rsp_Code(Enum):
    CONFIG            = b"\x01"
    NOTIFY            = b"\x02"
    READ_CONFIG       = b"\x03"
    ERROR_UNSUPPORTED = b"\x10"
    ERROR_PARAMS      = b"\x11"

class Tdt_Tap_Type(Enum):
    STI = b"\x00" 
    STD = b"\x01"
    DT  = b"\x02"
    LT  = b"\x03"

def handle_tdt_rsp(tile: 'Tile', rsp_payload: bytes):
    tdt_rsp_code = rsp_payload[0:1]
    if tdt_rsp_code == Tdt_Rsp_Code.NOTIFY.value:
        tdt_tap_type = rsp_payload[1:2]        
        if tdt_tap_type == Tdt_Tap_Type.STI.value:
            tile._single_tap_evt.set()
            tile._single_tap_evt.clear()
        elif tdt_tap_type == Tdt_Tap_Type.DT.value:
            tile._double_tap_evt.set()
            tile._double_tap_evt.clear()
        else:
            print(f"Unhandled tdt_tap_type: {tdt_tap_type} of payload {rsp_payload}")
    else:
        print(f"Unhandled tdt_rsp_code: {tdt_rsp_code} of payload {rsp_payload}")