import discord
import Config
import asyncio
import datetime
import aiohttp
from discord.ext import commands
from TopsUpdater import Tops
from GhostFetcher import Ghost
from bs4 import BeautifulSoup as BS
import urllib

COMMAND_PREFIX = '!'

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
    "RSL NG":   "N64 Sherbet Land",
    "RSL":      "N64 Sherbet Land (Glitch)",
    "RSGB":     "GBA Shy Guy Beach",
    "RDS":      "DS Delfino Square",
    "RWS":      "GCN Waluigi Stadium",
    "RDH NG":   "DS Desert Hills",
    "RDH":      "DS Desert Hills (Shortcut)",
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
    """Bot that handles the BNL Tops"""

    def __init__(self):
        super().__init__()

        self.bnl = Tops("BNL.json")
        self.bg_task = self.loop.create_task(self.auto_update(3600))
        self.last_updated = datetime.datetime.utcnow()
        self.client = aiohttp.ClientSession()
    
    async def on_ready(self):
        print("logged in")
        pass

    async def on_message(self, msg):
        """analyze all messages sent"""

        if msg.author == self.user:
            return

        if msg.channel.id != Config.CHANNEL:
            return

        contents = msg.content
        if contents[0] == COMMAND_PREFIX:
            split_msg = contents[1:].split(None, 1)

            # check all available commands
            if len(split_msg) > 1:
                if split_msg[1] == "help":
                    await self.command_info(msg, split_msg[0])
                elif split_msg[0] == "tops":
                    await self.tops(msg, split_msg[1])
            elif split_msg[0] == "help":
                await self.help(msg)
        else:
            return

    async def tops(self, msg, args):
        """tops command"""

        try:
            full_track = TRACK_ABBREVIATIONS[args.upper()]
            tops = self.bnl.get_top_10(full_track)

            message = "TOP10 {}\n".format(full_track)

            for pos, time in tops:
                message += "{}. {}\n".format(pos, time.to_str(markdown=True))

            await msg.channel.send(embed=self.create_tops_embed(full_track, tops))
        except KeyError:
            await msg.channel.send("Sorry, I don't know that track :disappointed:")

    async def help(self, msg):
        """help command"""

        embed = discord.Embed(title="**TT Bot commands**", colour=0x990000)

        message = """`!help`, `!tops`\n
                        To get more info on a command add `help`. E.g.: `!tops help`"""

        embed.add_field(name="I currently have these commands:", value=message, inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/556563172186914827/b483a54cb374449b6006954a8c469faa.png?size=128")

        await msg.channel.send(embed=embed)

    async def command_info(self, msg, command):
        """Provides info on a command"""

        message = ""
        if command == "help":
            await msg.channel.send(":thinking:")
        elif command == "tops":
            embed = discord.Embed(title="**!tops track category**", colour=0x990000)
            embed.add_field(name="track", value="track abbreviation, e.g.: `LC`, `rYF`", inline=False)
            embed.add_field(name="category", value="`ng` (no-glitch), `alt` (alternative).\n*Only add category if there are more than 1*", inline=False)
            await msg.channel.send(embed=embed)

    async def auto_update(self, loop_duration):
        """attempts to update the tops every (loop_duration) seconds"""

        await self.wait_until_ready()
        channel = self.get_channel(Config.CHANNEL)

        while not self.is_closed():
            await self.change_presence(activity=discord.Game(name="Checking Database"), status=discord.Status.idle)
            print("updating")
            times, changed = await self.bnl.update_tops(self.last_updated, self.client)
            #times = [("Koopa Cape", Ghost({"Country": '🇧🇪', "Name": "Olifré", "Time": "02:18.469", "Ghost": "http://www.chadsoft.co.uk/time-trials/rkgd/AF/6E/DBD745DB99D8853C2E21BB83AB13820A35BC.html"}), 3)]
            #self.bnl.add_time(times[0][1], times[0][0])
            #print(times)
            self.last_updated = datetime.datetime.utcnow()
            print("finished updating")

            if changed:
                #write to a new file so that changes can be reverted if necessary
                filename = "updated_tops/{}-{}-{}_{}:{}:{}.json".format(self.last_updated.year, self.last_updated.month, self.last_updated.day, self.last_updated.hour, self.last_updated.minute, self.last_updated.second)
                self.bnl.write_json(filename)
                self.bnl.write_json("./BNL.json")

            for time_info in times:
                await channel.send(embed=(self.create_update_embed(time_info)))

            await self.change_presence(activity=None, status=discord.Status.online)
            await asyncio.sleep(loop_duration)

    def create_tops_embed(self, track, tops):
        """formats the tops message"""

        embed = discord.Embed(title="**Top10 {}**".format(track), colour=0x4ccfff)

        """ Split the tops into the first 5, and everything else.
        This is done so that if the length of the 2 combined is more than 1024 characters (the field character limit),
        it can be broken down into 2 seperate fields."""
        message1 = ""
        message2 = ""
        index = 0
        for pos, time in tops:
            pos_str = str(pos)
            if len(pos_str) == 1:
                #alignment
                pos_str = '\u200B ' + pos_str
            if index < 5:
                message1 += "{}. {} {}: [{}]({})\n".format(pos_str, time.country, time.name, time.time, time.ghost)
            else:
                message2 += "{}. {} {}: [{}]({})\n".format(pos_str, time.country, time.name, time.time, time.ghost)

            index += 1

        if len(message1) + len(message2) > 1024:
            embed.add_field(name="\u200B", value=message1, inline=False)
            embed.add_field(name="\u200B", value=message2, inline=False)
        else:
            embed.add_field(name="\u200B", value=message1 + message2)

        return embed

    def create_update_embed(self, time_info):
        """formats the update message"""

        time = time_info[1]

        title = "{} ".format(time.name)
        if time_info[2] == 0 or time_info[2] == 1:
            title += "improved his time! Keep it up, proud of you"
        elif time_info[2] == 2:
            title += "enters the top 10! Welcome!"
        elif time_info[2] == 3:
            title += "claims first place! All hail the new king"
        elif time_info[2] == 4:
            title += "ties for 1st place! What are the chances?"

        field_title = "*{}*".format(time_info[0])

        # some easter eggs ;-)
        time_str = str(time.time)
        if time_str[-2:] == "69":
            time_str = time_str[:-2] + ":six::nine:"
        if time_str[-3:] == "420":
            time_str += " :fire::fire:"
        message = "{} {}: [{}]({})\n".format(time.country, time.name, time_str, time.ghost)


        embed = discord.Embed(title=title, colour=0x8eff56)
        embed.add_field(name=field_title, value=message)
        embed.set_thumbnail(url=self.extract_mii(time.ghost))
        return embed

    def extract_mii(self, link):
        """Extracts the url to the mii image file"""

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
    token = Config.TOKEN
    bot = Bot()
    bot.run(token)
