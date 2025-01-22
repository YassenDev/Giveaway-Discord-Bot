import sqlite3
import discord
import random
from discord.ext import tasks
from Utils.ButtonsEnd import ButtonEnd

async def Giveaway_Updater(client):
    cursor = client.db.cursor()
    cursor.execute("SELECT unique_id, channel_id, prize, hostedby, total, winners FROM Giveaway_Running WHERE running = ?", (1,))
    res = cursor.fetchall()

    if res:
        for x in res:
            channel = await client.fetch_channel(x[1])
            message = await channel.fetch_message(x[0])
            user = await client.fetch_user(x[3])

            hours, remainder = divmod(int(x[4] - 10), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)
            if days > 0:
                remaining_time = f"{days}d:{hours}h"
            elif hours > 0:
                remaining_time = f"{hours}h:{minutes}m"
            elif minutes > 0:
                remaining_time = f"{minutes}m:{seconds}s"
            else:
                remaining_time = f"{seconds}s"
            
            embed = discord.Embed(title="Giveaway Status", color=discord.Colour(0x36393e))
            embed.add_field(name="✨Prize", value=x[2], inline=True)
            embed.add_field(name="🙋‍♂️Hosted by", value=user.mention, inline=True)

            if x[4] - 10 <= 0:
                cursor.execute("SELECT user_id FROM Giveaway_Entry WHERE message_id = ?", (x[0],))
                entry_res = cursor.fetchall()

                if entry_res:
                    winners = []
                    if len(entry_res) < x[5]:
                        for _ in range(len(entry_res)):
                            n = random.choice(entry_res)
                            entry_res.remove(n)
                            winner = await client.fetch_user(n[0])
                            winners.append(winner)
                    else:
                        for _ in range(x[5]):
                            n = random.choice(entry_res)
                            entry_res.remove(n)
                            winner = await client.fetch_user(n[0])
                            winners.append(winner)

                    winners_mentions = "\n".join([winner.mention for winner in winners])
                    embed.add_field(name="🎊Winner(s)", value=winners_mentions or "Not enough Entries.", inline=True)
                    embed.set_footer(text="Ended")
                    await message.edit(content=":piñata:**__Giveaway Ended__**:piñata:", embed=embed, view=ButtonEnd(client))

                    # Add to Giveaways_Ended table
                    cursor.execute("INSERT INTO Giveaways_Ended (unique_id, guild_id, channel_id, prize, hostedby, total, winners) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                   (x[0], message.guild.id, x[1], x[2], x[3], x[4], ", ".join([str(winner.id) for winner in winners])))

                    cursor.execute("DELETE FROM Giveaway_Running WHERE unique_id = ?", (x[0],))

                    for winner in winners:
                        await channel.send(f"Congratulations {winner.mention}! You won the giveaway for {x[2]}!😃🎉")

                else:
                    embed.add_field(name="🎊Winner(s)", value="Not enough Entries.", inline=True)
                    embed.set_footer(text="Ended")
                    await message.edit(content=":piñata:**__Giveaway Ended__**:piñata:", embed=embed)

                    # Add to Giveaways_Ended table
                    cursor.execute("INSERT INTO Giveaways_Ended (unique_id, guild_id, channel_id, prize, hostedby, total) VALUES (?, ?, ?, ?, ?, ?)",
                                   (x[0], message.guild.id, x[1], x[2], x[3], x[4]))

                    cursor.execute("DELETE FROM Giveaway_Running WHERE unique_id = ?", (x[0],))
            else:
                if x[4] - 10 <= 60:
                    embed.add_field(name="⏲️Remaining Time", value=remaining_time, inline=True)
                else:
                    embed.add_field(name="⏲️Remaining Time", value=remaining_time, inline=True)

                await message.edit(embed=embed)
                cursor.execute("UPDATE Giveaway_Running SET total = total - 10 WHERE unique_id = ?", (x[0],))

    client.db.commit()
