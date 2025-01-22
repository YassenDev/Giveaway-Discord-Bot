import os
from pystyle import *



# Load Handler Commands
async def load_handler_commands(client):
    for filename in os.listdir("./Commands"):
        if filename.endswith(".py"):
            client.load_extension(f"Commands.{filename[:-3]}")
            print(f'Commands Loaded | {filename[:-3]}.py ✅')