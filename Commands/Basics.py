import discord
from discord.ext import commands


class Basics(commands.Cog):
    def __init__(self, client):
        self.client = client



    @commands.command(name="help")
    async def help(self, ctx: commands.Context):
        options = [
            discord.SelectOption(label="✨All Commands", value="1"),
            discord.SelectOption(label="🎊Giveaway", value="2"),
            discord.SelectOption(label="🔧Basics", value="3"),
        ]

        select_menu = discord.ui.Select(
            placeholder="Choose an option...",
            min_values=1,
            max_values=3,
            options=options,
        )

        select_menu.callback = self.on_select_option

        view = discord.ui.View()
        view.add_item(select_menu)

        embed = discord.Embed(title="📕Help Menu:", description="**😁Please choose an option from the select menu below.**")
        

        message = await ctx.reply(embed=embed, view=view)
        
    async def on_select_option(self, interaction):
        selected_value = interaction.data['values'][0]

        embed = discord.Embed()
        if selected_value == "1":
            embed.title = "📕Help Menu:"
            embed.add_field(name="🎊Giveaway Commands:", value=f"``start , running , resume\npause , end``", inline=False)
            embed.add_field(name="🔧Basics Commands:", value=f"``ping , help , status``", inline=False)
        elif selected_value == "2":
            embed.title = "📕Help Menu:"
            embed.add_field(name="🎊Giveaway Commands:", value=f"``start , running , resume\npause , end``", inline=False)
        elif selected_value == "3":
            embed.title = "📕Help Menu:"
            embed.add_field(name="🔧Basics Commands:", value=f"``ping , help , status``", inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command(name="status")
    async def status(self, ctx: commands.Context):
        websocket_latency = f"{round(self.client.latency * 1000)}ms"
        users = len(self.client.users)
        servers = len(self.client.guilds)
        created_at = self.client.user.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")

        embed = discord.Embed(
            title="🔧Status!",
            color=discord.Color.blue()
        )

        embed.add_field(name="⌛Websocket Latency", value=f"``{websocket_latency}``", inline=False)
        embed.add_field(name="🙋‍♂️Users", value=f"``{users}``", inline=False)
        embed.add_field(name="📕Servers", value=f"``{servers}``", inline=False)
        embed.add_field(name="✨Created at", value=f"``{created_at}``", inline=False)
        await ctx.reply(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        embed = discord.Embed(
            title="⌛Pong!",
            description=f"**🔧Latency: {round(self.client.latency * 1000)}ms**",
            color=discord.Color.blue()
        )

        await ctx.reply(embed=embed)


    @commands.command(name="about")
    async def about(self, ctx: commands.Context):
        embed = discord.Embed(
            title="About!",
            description=f"**A simple Discord giveaways bot to suit all of your needs!\nThis is a bot that provides all the necessary utilities to run a giveaway in Discord.\n\n\nIf You Need Help Join To DevXor : [Click Here](https://discord.gg/devxor-931536214228611102)**",
            color=discord.Color.blue()
        )

        await ctx.reply(embed=embed)





def setup(client):
    client.add_cog(Basics(client))
