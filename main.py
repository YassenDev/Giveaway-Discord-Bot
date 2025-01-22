import sqlite3, discord
from discord.ext import commands, tasks
from config import TOKEN, PREFIX
from pystyle import *
from Utils.Giveaway_Updater import Giveaway_Updater
from Handler.load_commands import load_handler_commands
from Handler.load_utils import load_handler_utils
from Utils.Button import Button


client = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all(), help_command=None)

# Event On Ready
@client.event
async def on_ready():
    started = r"""
   ___           _  __           ___             _         __ 
  / _ \___ _  __| |/_/__  ____  / _ \_______    (_)__ ____/ /_
 / // / -_) |/ />  </ _ \/ __/ / ___/ __/ _ \  / / -_) __/ __/
/____/\__/|___/_/|_|\___/_/   /_/  /_/  \___/_/ /\__/\__/\__/ 
                                           |___/              
    """
    print(Colorate.Horizontal(Colors.yellow_to_red, text=started, cut=1))
    print(f'Bot Loaded | {client.user}✅')
    client.db = sqlite3.connect("database.sqlite") 
    cursor = client.db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Giveaway_Entry (user_id INTEGER, message_id INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Giveaway_Running (unique_id INTEGER, guild_id INTEGER, channel_id INTEGER, prize TEXT, hostedby INTEGER, total REAL, running INTEGER, entries INTEGER, winners INTEGER, PRIMARY KEY (unique_id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS Giveaways_Ended (unique_id INTEGER, guild_id INTEGER, channel_id INTEGER, prize TEXT, hostedby INTEGER, total REAL, winners TEXT)")
    cursor.execute("SELECT unique_id, channel_id, prize, total FROM Giveaway_Running WHERE running = ?", (1,))
    res = cursor.fetchall()

    for giveaway in res:
        channel = await client.fetch_channel(giveaway[1])
        message = await channel.fetch_message(giveaway[0])
        button_view = Button(client)
        await message.edit(view=button_view)

    cursor.close()
    client.db.commit()
    Giveaway_Updater_Task.start()
    await load_handler_commands(client)
    await load_handler_utils(client)

@tasks.loop(seconds=10)
async def Giveaway_Updater_Task():
    await Giveaway_Updater(client)


# Client Run
client.run(TOKEN)

