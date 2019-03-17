import discord
import config
import asyncio
import datetime
from discord.ext import commands
from TopsUpdater import Tops
from GhostFetcher import Ghost
from bs4 import BeautifulSoup as BS
import urllib

COMMAND_PREFIX = '$'

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

class Bot(discord.Client):

    def __init__(self):
        super().__init__()

        self.bnl = Tops("BNL.json")
        self.bg_task = self.loop.create_task(self.auto_update(10))
    
    async def on_ready(self):
        pass

    async def on_message(self, msg):
        if msg.author == self.user:
            return

        contents = msg.content
        if contents[0] == '$':
            split_msg = contents[1:].split(None, 1)

            # check all available commands
            if split_msg[0] == "tops":
                await self.tops(msg, split_msg[1])
        else:
            return

    async def tops(self, msg, args):
        full_track = TRACK_ABBREVIATIONS[args.upper()] 
        tops = self.bnl.get_top_10(full_track)

        message = "TOP10 {}\n".format(full_track)

        for pos, time in tops:
            message += "{}. {}\n".format(pos, time.to_str(markdown=True))

        await msg.channel.send(embed=self.create_tops_embed(tops, full_track))

    async def auto_update(self, loop_duration):
        await self.wait_until_ready()
        channel = self.get_channel(config.CHANNEL)

        while not self.is_closed():
            print("started task")
            #times = self.bnl.update_tops()
            times = [("Koopa Cape", Ghost({"Country": '🇧🇪', "Name": "Olifré", "Time": "02:17.999", "Ghost": "http://www.chadsoft.co.uk/time-trials/rkgd/AF/6E/DBD745DB99D8853C2E21BB83AB13820A35BC.html"}), 3)]

            for time_info in times:
                await channel.send(embed=(self.create_update_embed(time_info)))

            await asyncio.sleep(loop_duration)

    def create_tops_embed(self, track):
        embed = discord.Embed(title="**Top10 {}**".format(track), colour=0x4ccfff)

        message = ""
        for pos, time in self.tops:
            pos_str = str(pos)
            if len(pos_str) == 1:
                pos_str = '\u200B ' + pos_str

            message += "{}. {} {}: [{}]({})\n".format(pos_str, time.country, time.name, time.time, time.ghost)

        embed.add_field(name="\u200B", value=message, inline=True)
        return embed

    def create_update_embed(self, time_info):
        time = time_info[1]

        title = "{} ".format(time.name)
        if time_info[2] == 1:
            title += "improved his time! Keep it up, proud of you"
        elif time_info[2] == 2:
            title += "enters the top 10! Welcome!"
        elif time_info[2] == 3:
            title += "claims first place! All hail the new king"
        elif time_info[2] == 4:
            title += "ties for 1st place! What are the chances?"

        field_title = "*{}*".format(time_info[0])
        message = "{} {}: [{}]({})\n".format(time.country, time.name, time.time, time.ghost)


        embed = discord.Embed(title=title, colour=0x8eff56)
        embed.add_field(name=field_title, value=message)
        embed.set_thumbnail(url=self.extract_mii(time.ghost))
        return embed

    def extract_mii(self, link):
        """Extracts the url to the mii image file"""
        print("hello there")
        html = urllib.request.urlopen(link)
        soup = BS(html, features="html5lib")
        parent_div = soup.findAll("div", class_="_1c5")[0]
        child_div = parent_div.contents[1]
        div_str = str(child_div)

        start = div_str.find("url('") + 5
        end = div_str.find("')", start)
        mii = div_str[start:end]

        return "http://www.chadsoft.co.uk" + mii


if __name__ == "__main__":
    token = config.TOKEN
    bot = Bot()
    bot.run(token)