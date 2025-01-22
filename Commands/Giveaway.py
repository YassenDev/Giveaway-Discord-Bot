import discord
import random
from discord.ext import commands
import sqlite3
from Utils.Button import Button
from Utils.TimeConverter import TimeConverter
from Utils.ButtonsEnd import ButtonEnd

# Giveaway Commands
class Giveaway(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.db = sqlite3.connect("database.sqlite")

    # Start Command
    @commands.command()
    async def start(self, ctx, GiveawayDuration: TimeConverter = None, winner=None, *, prize=None):
        if not ctx.author.guild_permissions.administrator:
              await ctx.send("You do not have permission to use this command❌.")
              return

        cursor = self.client.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM Giveaway_Running WHERE running = ? AND guild_id = ?", (1, ctx.guild.id))
        running_giveaways_count = cursor.fetchone()[0]

        if running_giveaways_count >= 20:
            await ctx.send("Sorry, you cannot start more than 20 giveaways simultaneously.")
            return

        if GiveawayDuration is None:
            await ctx.send("Please specify the duration of the giveaway.")
            return
        if winner is None:
            await ctx.send("Please specify the number of winners for the giveaway.")
            return
        if prize is None:
            await ctx.send("Please specify the prize for the giveaway.")
            return

        hours, remainder = divmod(int(GiveawayDuration), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if days > 0:
            duration_str = f"{days}d:{hours}h"
        elif hours > 0:
            duration_str = f"{hours}h:{minutes}m"
        elif minutes > 0:
            duration_str = f"{minutes}m:{seconds}s"
        else:
            duration_str = f"{seconds}s"

        embed = discord.Embed(title="🎉 **Giveaway Started** 🎉", color=discord.Colour(0x36393e))
        embed.add_field(name="✨Prize", value=prize, inline=True)
        embed.add_field(name="🙋‍♂️Hosted by", value=ctx.author.mention, inline=True)
        embed.add_field(name="⏲️Duration", value=duration_str, inline=True)

        message = await ctx.send(content=":loudspeaker:**__Giveaway Started__**:loudspeaker:", embed=embed, view=Button(self.client))

        cursor.execute("INSERT OR IGNORE INTO Giveaway_Running (unique_id, guild_id, channel_id, prize, hostedby, total, running, entries, winners) VALUES (?,?,?,?,?,?,?,?,?)",
                        (message.id, ctx.guild.id, ctx.channel.id, prize, ctx.author.id, GiveawayDuration, 1, 0, winner))
        self.client.db.commit()

    # Pause Command
    @commands.command()
    async def pause(self, ctx):
        if not ctx.author.guild_permissions.administrator:
              await ctx.send("You do not have permission to use this command❌.")
              return

        cursor = self.client.db.cursor()
        cursor.execute("SELECT unique_id, prize FROM Giveaway_Running WHERE running = ? AND guild_id = ?", (1, ctx.guild.id))
        res = cursor.fetchall()

        if res:
            options = [discord.SelectOption(label=f"{row[1][:10]}", value=str(row[0])) for row in res]  
            select_menu = discord.ui.Select(
                placeholder="Select a giveaway to pause...",
                options=options
            )
            view = discord.ui.View()
            view.add_item(select_menu)

            async def pause_callback(interaction):
                giveaway_id = int(interaction.data["values"][0])
                cursor.execute("UPDATE Giveaway_Running SET running = ? WHERE unique_id = ? AND guild_id = ?", (0, giveaway_id, ctx.guild.id))
                self.client.db.commit()

                cursor.execute("SELECT unique_id, channel_id, prize, hostedby, total FROM Giveaway_Running WHERE unique_id = ?", (giveaway_id,))
                res = cursor.fetchone()

                ch = self.client.get_channel(res[1])
                ms = await ch.fetch_message(res[0])
                user = self.client.get_user(res[3])
                embed = discord.Embed(description=f"**{res[2]}**\n\nHosted by: {user.mention}\n\nPaused", colour=discord.Colour(0x36393e))
                await ms.edit(embed=embed)

                await interaction.response.send_message("Giveaway paused successfully!", ephemeral=True)

            select_menu.callback = pause_callback

            embed = discord.Embed(
                title="Pause Giveaway",
                description="Please select a giveaway to pause:",
                color=discord.Color.blurple()
            )
            message = await ctx.send(embed=embed, view=view)
        else:
            await ctx.send("There are no running giveaways to pause.")

    # Resume Command
    @commands.command()
    async def resume(self, ctx):
        if not ctx.author.guild_permissions.administrator:
              await ctx.send("You do not have permission to use this command❌.")
              return

        cursor = self.client.db.cursor()
        cursor.execute("SELECT unique_id, prize FROM Giveaway_Running WHERE running = ? AND guild_id = ?", (0, ctx.guild.id))
        res = cursor.fetchall()

        if res:
            options = [discord.SelectOption(label=f"{row[1][:10]}", value=str(row[0])) for row in res]  
            select_menu = discord.ui.Select(
                placeholder="Select a giveaway to resume...",
                options=options
            )
            view = discord.ui.View()
            view.add_item(select_menu)

            async def resume_callback(interaction):
                giveaway_id = int(interaction.data["values"][0])
                cursor.execute("UPDATE Giveaway_Running SET running = ? WHERE unique_id = ? AND guild_id = ?", (1, giveaway_id, ctx.guild.id))
                self.client.db.commit()

                await interaction.response.send_message("Giveaway resumed successfully!", ephemeral=True)

            select_menu.callback = resume_callback

            embed = discord.Embed(
                title="Resume Giveaway",
                description="Please select a giveaway to resume:",
                color=discord.Color.blurple()
            )
            message = await ctx.send(embed=embed, view=view)
        else:
            await ctx.send("There are no paused giveaways to resume.")

    # Running Command
    @commands.command()
    async def running(self, ctx):
        if not ctx.author.guild_permissions.administrator:
              await ctx.send("You do not have permission to use this command❌.")
              return
            
        cursor = self.client.db.cursor()
        cursor.execute("SELECT unique_id, prize FROM Giveaway_Running WHERE running = ? AND guild_id = ?", (1, ctx.guild.id))
        res = cursor.fetchall()

        if res:
            options = [discord.SelectOption(label=f"{row[1][:10]}", value=str(row[0])) for row in res] 
            select_menu = discord.ui.Select(
                placeholder="Select a running giveaway...",
                options=options
            )
            view = discord.ui.View()
            view.add_item(select_menu)

            async def select_callback(interaction):
                selected_giveaway_id = int(interaction.data["values"][0])
                cursor.execute("SELECT channel_id, prize, hostedby, total FROM Giveaway_Running WHERE unique_id = ? AND guild_id = ?", (selected_giveaway_id, ctx.guild.id))
                giveaway_info = cursor.fetchone()

                if giveaway_info:
                    channel_id, prize, hostedby, total = giveaway_info
                    channel = self.client.get_channel(channel_id)
                    host = self.client.get_user(hostedby)

                    embed = discord.Embed(title="Giveaway Information", color=discord.Colour(0x36393e))
                    embed.add_field(name="Prize", value=prize, inline=False)
                    embed.add_field(name="Hosted by", value=host.mention, inline=False)
                    embed.add_field(name="Time Remaining", value=f"{total}s", inline=False)

                    await interaction.response.send_message(content="Here is the information for the selected giveaway:", embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_message("Couldn't find information for the selected giveaway.", ephemeral=True)

            select_menu.callback = select_callback

            embed = discord.Embed(
                title="Running Giveaways",
                description="Please select a running giveaway to view its information:",
                color=discord.Color.blurple()
            )
            message = await ctx.send(embed=embed, view=view)
        else:
            await ctx.send("There are no running giveaways.")

    # End Command
    @commands.command()
    async def end(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have permission to use this command❌.")
            return

        cursor = self.client.db.cursor()
        cursor.execute("SELECT unique_id, prize FROM Giveaway_Running WHERE running = ? AND guild_id = ?", (1, ctx.guild.id))
        res = cursor.fetchall()

        if not res:
            await ctx.send("There are no running giveaways to end.")
            return

        options = [discord.SelectOption(label=row[1][:10], value=str(row[0])) for row in res]

        class EndSelect(discord.ui.Select):
            def __init__(self, client):
                super().__init__(placeholder="Select a giveaway to end...", options=options)
                self.client = client

            async def callback(self, interaction: discord.Interaction):
                giveaway_id = int(self.values[0])

                cursor.execute("SELECT * FROM Giveaway_Running WHERE unique_id = ? AND guild_id = ?", (giveaway_id, ctx.guild.id))
                giveaway = cursor.fetchone()

                if not giveaway:
                    await interaction.response.send_message("No running giveaway found with the provided unique ID.", ephemeral=True)
                    return

                channel = await self.client.fetch_channel(giveaway[2])
                message = await channel.fetch_message(giveaway[0])
                embed = discord.Embed(title="Giveaway Ended", color=discord.Colour.red())
                embed.description = "This giveaway has been manually ended by an administrator."
                await message.edit(content=":piñata: **__Giveaway Ended__** :piñata:", embed=embed, view=ButtonEnd(self.client))

                cursor.execute("UPDATE Giveaway_Running SET running = 0 WHERE unique_id = ?", (giveaway_id,))
                self.client.db.commit()

                await interaction.response.send_message("The giveaway has been successfully ended.", ephemeral=True)

        class EndView(discord.ui.View):
            def __init__(self, client):
                super().__init__()
                self.add_item(EndSelect(client))

        embed = discord.Embed(
            title="End Giveaway",
            description="Please select a running giveaway to end:",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed, view=EndView(self.client))





def setup(client):
    client.add_cog(Giveaway(client))
