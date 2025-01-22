import re
from discord.ext import commands


# TimeConverter
time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            if k not in time_dict:
                await ctx.send(f"{k} is an invalid time-key! h/m/s/d are valid!❌")
                return None
            try:
                time += time_dict[k] * float(v)
            except ValueError:
                await ctx.send(f"{v} is not a number!")
                return None
        if time == 0:
            await ctx.send("Time is an invalid time-key! h/m/s/d are valid!❌")
            return None
        return time

