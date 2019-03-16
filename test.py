import discord
import token
from discord.ext import commands
from TopsUpdater import Tops

TRACK_ABBREVIATIONS = {
    "LC":       "Luigi Circuit",
    "MMM":      "Moo Moo Meadows",
    "MG ng":    "Mushroom Gorge",
    "MG":       "Mushroom Gorge (Glitch)",
    "TF":       "Toad's Factory",
    "MC ng":    "Mario Circuit",
    "MC":       "Mario Circuit (Glitch)",
    "CM ng":    "Coconut Mall",
    "CM":       "Coconut Mall (Glitch)",
    "DKS":      "DK Summit",
    "WGM ng":   "Wario's Gold Mine",
    "WGM":      "Wario's Gold Mine (Glitch)",
    "DC":       "Daisy Circuit",
    "KC":       "Koopa Cape",
    "MT ng":    "Maple Treeway",
    "MT":       "Maple Treeway (Glitch)",
    "GV ng":    "Grumble Volcano",
    "GV alt":   "Grumble Volcano (Shortcut)",
    "GV":       "Grumble Volcano (Glitch)",
    "DDR":      "Dry Dry Ruins",
    "MH":       "Moonview Highway",
    "BC ng":    "Bowser's Castle",
    "BC":       "Bowser's Castle (Glitch)",
    "RR":       "Rainbow Road",
    "rPB ng":   "GCN Peach Beach",
    "rPB":      "GCN Peach Beach (Glitch)",
    "rYF":      "DS Yoshi Falls",
    "rGV2 ng":  "SNES Ghost Valley 2",
    "rGV2":     "SNES Ghost Valley 2 (Glitch)",
    "rMR":      "N64 Mario Raceway",
    "rSL ng":   "N64 Sherbet Land",
    "rSL":      "N64 Sherbet Land (Glitch)",
    "rSGB":     "GBA Shy Guy Beach",
    "rDS":      "DS Delfino Square",
    "rWS":      "GCN Waluigi Stadium",
    "rDH ng":   "DS Desert Hills",
    "rDH":      "DS Desert Hills (Glitch)",
    "rBC3 ng":  "GBA Bowser Castle 3",
    "rBC3":     "GBA Bowser Castle 3 (Shortcut)",
    "rDKJP ng": "N64 DK Jungle Parkway",
    "rDKJP alt":"N64 DK Jungle Parkway (Shortcut)",
    "rDKJP":    "N64 DK Jungle Parkway (Glitch)",
    "rMC":      "GCN Mario Circuit",
    "rMC3":     "SNES Mario Circuit 3",
    "rPG":      "DS Peach Gardens",
    "rDKM ng":  "GCN DK Mountain",
    "rDKM":     "GCN DK Mountain (Shortcut)",
    "rBC":      "N64 Bowser's Castle"
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

    async def on_ready(self):
        print("Logged in as")
        print(self.bot.user.name)
        print(self.bot.user.id)
    
    @commands.command()
    async def tops(self, ctx, track, category=None):
        print(track)
        if category:
            track += ' ' + category

        full_track = TRACK_ABBREVIATIONS[track] 
        tops = self.bnl.get_top_10(full_track)

        message = "Top10 {}\n".format(full_track)
        print(message)
        print(tops)

        for pos, time in tops:
            message += "{}. {}\n".format(pos, time.to_str(markdown=True))

        await ctx.send(embed=create_tops_embed(tops, full_track))

    async def tops(self, ctx, track, category=None):

if __name__ == "__main__":
    bot = commands.Bot(command_prefix='$')
    bot.add_cog(Messages(bot))
    token = TOKEN
    bot.run(token)