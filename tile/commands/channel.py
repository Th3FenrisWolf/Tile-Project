from toa import Toa_Cmd_Code, send_connectionless_cmd

def open_channel(mac_address):
    return send_connectionless_cmd(mac_address, Toa_Cmd_Code.OPEN_CHANNEL, rand_a)