import discord
import config
import asyncio
import datetime
from discord.ext import commands
from TopsUpdater import Tops

TRACK_ABBREVIATIONS = {
    "LC":       "Luigi Circuit",
    "MMM":      "Moo Moo Meadows",
    "MG NG":    "Mushroom Gorge",
    "MG":       "Mushroom Gorge (Glitch)",
    "TF":       "Toad's Factory",
    "MC NG":    "Mario Circuit",
    "MC":       "Mario Circuit (Glitch)",
    "CM NG":    "Coconut Mall",
    "CM":       "Coconut Mall (Glitch)",
    "DKS":      "DK Summit",
    "WGM NG":   "Wario's Gold Mine",
    "WGM":      "Wario's Gold Mine (Glitch)",
    "DC":       "Daisy Circuit",
    "KC":       "Koopa Cape",
    "MT NG":    "Maple Treeway",
    "MT":       "Maple Treeway (Glitch)",
    "GV NG":    "Grumble Volcano",
    "GV ALT":   "Grumble Volcano (Shortcut)",
    "GV":       "Grumble Volcano (Glitch)",
    "DDR":      "Dry Dry Ruins",
    "MH":       "Moonview Highway",
    "BC NG":    "Bowser's Castle",
    "BC":       "Bowser's Castle (Glitch)",
    "RR":       "Rainbow Road",
    "RPB NG":   "GCN Peach Beach",
    "RPB":      "GCN Peach Beach (Glitch)",
    "RYF":      "DS Yoshi Falls",
    "RGV2 NG":  "SNES Ghost Valley 2",
    "RGV2":     "SNES Ghost Valley 2 (Glitch)",
    "RMR":      "N64 Mario Raceway",
    "RSL ng":   "N64 Sherbet Land",
    "RSL":      "N64 Sherbet Land (Glitch)",
    "RSGB":     "GBA Shy Guy Beach",
    "RDS":      "DS Delfino Square",
    "RWS":      "GCN Waluigi Stadium",
    "RDH NG":   "DS Desert Hills",
    "RDH":      "DS Desert Hills (Glitch)",
    "RBC3 NG":  "GBA Bowser Castle 3",
    "RBC3":     "GBA Bowser Castle 3 (Shortcut)",
    "RDKJP NG": "N64 DK Jungle Parkway",
    "RDKJP ALT":"N64 DK Jungle Parkway (Shortcut)",
    "RDKJP":    "N64 DK Jungle Parkway (Glitch)",
    "RMC":      "GCN Mario Circuit",
    "RMC3":     "SNES Mario Circuit 3",
    "RPG":      "DS Peach Gardens",
    "RDKM NG":  "GCN DK Mountain",
    "RDKM":     "GCN DK Mountain (Shortcut)",
    "RBC":      "N64 Bowser's Castle"
}

def create_tops_embed(tops, track):
    embed = discord.Embed(title="**Top10 {}**".format(track), colour=0x4ccfff)

    message = ""
    for pos, time in tops:
        pos_str = str(pos)
        if len(pos_str) == 1:
            pos_str = '\u200B ' + pos_str

        message += "{}. {} {}: [{}]({})\n".format(pos_str, time.country, time.name, time.time, time.ghost)

    embed.add_field(name="\u200B", value=message, inline=True)
    return embed

class Messages(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bnl = Tops("BNL.json")
        self.bg_task = discord.Client.loop.create_task(self.update_times(5))

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            print(guild.name)
    
    @commands.command()
    async def tops(self, ctx, *, track):
        full_track = TRACK_ABBREVIATIONS[track.upper()] 
        tops = self.bnl.get_top_10(full_track)

        message = "TOP10 {}\n".format(full_track)

        for pos, time in tops:
            message += "{}. {}\n".format(pos, time.to_str(markdown=True))

        await ctx.send(embed=create_tops_embed(tops, full_track))          

if __name__ == "__main__":
    bot = commands.Bot(command_prefix='$')
    bot.add_cog(Messages(bot))
    token = config.TOKEN
    bot.run(token)