#class Songs(enum.IntEnum)
#class Ring(Command)

class Songs:
    CLICK_1      = 0x00
    FIND         = 0x01
    ACTIVE       = 0x02
    SLEEP        = 0x03
    WAKEUP       = 0x04
    FACTORY_TEST = 0x05
    MYSTERY      = 0x06
    SILENT       = 0x07
    BUTTON       = 0x08
    WAKEUP_PART  = 0x09
    DT_SUCCESS   = 0x0a
    DT_FAILURE   = 0x0b
    CLICK_2      = 0x0c
    BIP_1        = 0x0d
    BIP_2        = 0x0e
    BIP_3        = 0x0f
    BIP_4        = 0x10
    BIP_5        = 0x11
    BIP_6        = 0x12
    BIP_7        = 0x13
    DT_HB        = 0x14
    MAX          = 0x15
    STOP         = 0xFF

# the implicit duration is 0xfe, which appears to just play the song in its entirety
# strength ranges from 0-3, where 0 is silent and 3 is loudest
# according to tile_song_module.h:214
async def play_song(self, number: int, strength: int) -> None:
    # check that client has been set
    assert self.client is not None, "Client is not set"
    # check that session_key has been set
    assert self.session_key is not None, "Channel must be opened, call open_channel_rsp_callback before this method"
    # check that allocated_cid has been set
    assert self.allocated_cid is not None, "Channel must be opened, call open_channel_rsp_callback before this method"

    # assert correct input parameters
    assert 0 <= strength <= 3, "Strength must have a value in the range of 0-3"

    # first byte is the command
    toa_cmd_code = Toa_Cmd_Code.SONG.to_bytes(1, byteorder='big')
    
    # second byte is the number
    numberByte = number.to_bytes(1, byteorder='big')
    
    # third byte is the strength
    strengthByte = strength.to_bytes(1, byteorder='big')

    toa_cmd_payload = b"\x02" + numberByte + strengthByte
    
    # necessary for MIC calculations
    MAX_PAYLOAD_LEN = 22
    toa_cmd_code_and_payload_len = (len(toa_cmd_code) + len(toa_cmd_payload)).to_bytes(1, byteorder='big')
    toa_cmd_padding = (MAX_PAYLOAD_LEN - len(toa_cmd_code) - len(toa_cmd_payload)) * b"\0"
    new_message = b"\x01" + b"\x00" * 7 + b"\x01" + toa_cmd_code_and_payload_len + toa_cmd_code + toa_cmd_payload + toa_cmd_padding 
    mic = hmac.new(self.session_key, msg=new_message, digestmod = hashlib.sha256).digest()[:4]
    play_song = self.allocated_cid + toa_cmd_code + toa_cmd_payload + mic

    await self.client.write_gatt_char(TILE_TOA_CMD_UUID, play_song)