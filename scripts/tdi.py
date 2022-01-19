#sending 1303 (\x00\x00\x00\x00\x00\x13\x03) returns \x00\x00\x00\x00\x00\x14\x0325.04.06.0
class TDI_CMD(Enum):
  TILE_ID     = b"\x02"
  FM_VERSION  = b"\x03"
  MODEL_NUM   = b"\x04"
  HW_VERSION  = b"\x05"
  MAC_ADDR    = b"\x06"

loop = asyncio.get_event_loop()
coroutine = async_func()
loop.run_until_complete(coroutine)