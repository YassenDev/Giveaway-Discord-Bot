import discord

# Button
class Button(discord.ui.View):
    def __init__(self, client, *, timeout=180):
        super().__init__(timeout=None)
        self.client = client
        self.giveaway_ended = False 
        
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
    @discord.ui.button(label="Join", custom_id="Joiner", style=discord.ButtonStyle.green, emoji="✅")
    async def Join_Button(self, button: discord.ui.Button, interaction: discord.Interaction):
        message_id = int(interaction.message.id)

        cursor = self.client.db.cursor()
        cursor.execute("SELECT user_id FROM Giveaway_Entry WHERE message_id = ?", (interaction.message.id,))
        res = cursor.fetchall()

        if res:
            for x in res:
                if interaction.user.id == x[0]:
                    return await interaction.response.send_message("You already entered this Giveaway.❌", ephemeral=True)

        cursor.execute("UPDATE Giveaway_Running SET entries = entries + ? WHERE unique_id = ?", (1, int(interaction.message.id),))
        self.client.db.commit()

        cursor.execute("SELECT entries FROM Giveaway_Running WHERE unique_id = ?", (interaction.message.id,))
        res = cursor.fetchone()

        if res is not None:
            entries = res[0]
            self.children[0].label = f"Joined: {entries}"
            cursor.execute("INSERT OR IGNORE INTO Giveaway_Entry (user_id, message_id) VALUES (?,?)", (interaction.user.id, interaction.message.id))
            self.client.db.commit()
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.send_message("Sorry, this giveaway has ended.❌", ephemeral=True)


    # Leaver Button
    @discord.ui.button(label="Leave", custom_id="Leaver", style=discord.ButtonStyle.red, emoji="✖️")
    async def Leave_Button(self, button: discord.ui.Button, interaction: discord.Interaction):
        cursor = self.client.db.cursor()
        cursor.execute("SELECT user_id FROM Giveaway_Entry WHERE message_id = ?", (interaction.message.id,))
        res = cursor.fetchall()

        if res:
            for x in res:
                if interaction.user.id == x[0]:
                    cursor.execute("DELETE FROM Giveaway_Entry WHERE user_id = ? AND message_id = ?", (interaction.user.id, interaction.message.id))
                    self.client.db.commit()

                    cursor.execute("SELECT entries FROM Giveaway_Running WHERE unique_id = ?", (interaction.message.id,))
                    res = cursor.fetchone()
                    if res:
                        entries = res[0] - 1  
                        cursor.execute("UPDATE Giveaway_Running SET entries = ? WHERE unique_id = ?", (entries, interaction.message.id))
                        self.client.db.commit()

                        self.children[0].label = f"Joined: {entries}"
                        await interaction.message.edit(view=self)
                        await interaction.response.send_message("You've successfully left the giveaway.✔", ephemeral=True)
                        return

        await interaction.response.send_message("You haven't joined this giveaway yet.❌", ephemeral=True)