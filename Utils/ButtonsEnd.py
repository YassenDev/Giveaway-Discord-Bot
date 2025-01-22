import discord

# ButtonEnd
class ButtonEnd(discord.ui.View):
    def __init__(self, client, giveaway_ended=False, *, timeout=180):
        super().__init__(timeout=None)
        self.client = client
        self.giveaway_ended = giveaway_ended

    # Entry Button
    @discord.ui.button(label=f"Joined: 0", custom_id="Entry", style=discord.ButtonStyle.grey, emoji="🙋‍♂️", disabled=False)
    async def Entry_Button(self, button2: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("You do not have permission to view the entries of this giveaway.❌", ephemeral=True)

        message_id = interaction.message.id

        cursor = self.client.db.cursor()
        cursor.execute("SELECT user_id FROM Giveaway_Entry WHERE message_id = ?", (message_id,))
        res = cursor.fetchall()

        if res:
            user_mentions = []
            for user_id in res:
                user = await self.client.fetch_user(user_id[0])
                user_mentions.append(user.mention)

            embed = discord.Embed(title="User Entries", color=0x00ff00)
            embed.add_field(name="Entries", value="\n".join(user_mentions), inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("No users have entered this giveaway yet.❌", ephemeral=True)

    # Joiner Button
    @discord.ui.button(label="Join", custom_id="Joiner", style=discord.ButtonStyle.green, emoji="✅", disabled=True)
    async def Join_Button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("The giveaway has ended, you can no longer join.❌", ephemeral=True)

    # Leaver Button
    @discord.ui.button(label="Leave", custom_id="Leaver", style=discord.ButtonStyle.red, emoji="✖️", disabled=True)
    async def Leave_Button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("The giveaway has ended, you can no longer leave.❌", ephemeral=True)



