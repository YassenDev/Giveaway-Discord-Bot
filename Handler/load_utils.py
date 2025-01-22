import os
from pystyle import *


# Load Handler Utils
async def load_handler_utils(client):
    for filename in os.listdir("./Utils"):
        if filename.endswith(".py"):
            print(f'Utils Loaded | {filename[:-3]}.py ✅')