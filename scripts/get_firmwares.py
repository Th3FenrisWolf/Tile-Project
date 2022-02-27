from torrequest import TorRequest
import itertools
from time import time

with TorRequest() as tr:
    response = tr.get('http://ipecho.net/plain')
    print(response.text)  # not your IP address

    for a,b,c,d in itertools.product(range(0,100), range(100), range(100), range(10)):
        local_filename = f"Tile_FW_Image_{a:02d}.{b:02d}.{c:02d}.{d}.bin"

        r = tr.get(f"https://s3.amazonaws.com/tile-tofu-fw/prod/{local_filename}", stream=True)
        
        if int(time()) % 60 == 0:
            print(f"Currenty trying {local_filename}")

        if "AccessDenied" in r.text:
            continue
        else:
            print("got ", local_filename)
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()