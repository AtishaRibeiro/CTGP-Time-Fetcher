import discord
import Config
import asyncio
import datetime
import aiohttp
from DB import DB
from TopsUpdater import Tops
from GhostFetcher import Ghost, FinishTime
from bs4 import BeautifulSoup as BS
import urllib

COMMAND_PREFIX = '!'

class Bot(discord.Client):
    """Bot that handles the BNL Tops and more"""

    def __init__(self):
        super().__init__()

        self.DB = DB("tt_bot_db.db")
        self.bnl = Tops(self.DB)
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
            command = split_msg[0]

            # check all available commands
            if len(split_msg) > 1:
                if split_msg[1] == "help":
                    await self.command_info(msg, split_msg[0])
                elif command == "tops":
                    await self.tops(msg, split_msg[1])
                elif command == "count":
                    await self.count(msg, split_msg[1])
                elif command == "pb":
                    await self.pb(msg, split_msg[1].split())
            elif command == "help":
                await self.help(msg)
            elif command == "links":
                await self.links(msg)
        else:
            return

    async def tops(self, msg, args):
        """tops command"""

        try:
            full_track = self.DB.get_track_name(args.upper())[0]
            tops = self.bnl.get_top_10(full_track)
            await msg.channel.send(embed=self.create_tops_embed(full_track, tops))
        except TypeError:
            await msg.channel.send("Sorry, I don't know that track :disappointed:")

    async def help(self, msg):
        """help command"""

        embed = discord.Embed(title="**TT Bot commands**", colour=0x990000)

        message = "`!help`, `!tops`, `!count`, `!pb`, `!links`\n" \
                    "To get more info on a command add `help`. E.g.: `!tops help`"

        embed.add_field(name="I currently have these commands:", value=message, inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/556563172186914827/b483a54cb374449b6006954a8c469faa.png?size=128")

        await msg.channel.send(embed=embed)

    async def links(self, msg):
        """links command"""

        embed = discord.Embed(title="**Useful Links**", colour=0x990000)

        message = "- [CTGP-R Database](http://www.chadsoft.co.uk/time-trials/) regular and custom track leaderboards\n" \
                    "- [MKLeaderboards](https://www.mkleaderboards.com/mkw) various top 10's\n" \
                    "- [MKW WR history](https://mkwrs.com/mkwii/) all current and past world records\n" \
                    "- [Player Page](http://www.mariokart64.com/mkw/wrc.php) mkwii player page\n" \
                    "- [CTGP Records Channel](https://www.youtube.com/channel/UCxCPLtXIg43HRP6QZN8gyYQ/featured) video uploads of world records\n" \
                    "- [Tas WR's](http://mkwtas.com/) all current TAS world records"

        embed.add_field(name="\u200B", value=message)
        await msg.channel.send(embed=embed)

    async def count(self, msg, player):
        """provides the amount of times a player appears in the leaderboards"""

        embed = discord.Embed(title="**BNL Leaderboard appearances**", colour=0xffffff)
        total_count, ng_count, glitch_count, alt_count = self.DB.get_player_count(player)

        message = "**{}/32** *no-glitch*\n**{}/14** *glitch*\n**{}/2** *alternate*".format(ng_count, glitch_count, alt_count)

        embed.add_field(name="`{}` appears **{}** time(s) in the leaderboards".format(player, total_count), value=message)
        await msg.channel.send(embed=embed)

    async def pb(self, msg, args):
        """gives the personal best for a player"""

        track = ""
        player = ""
        if args[-1] == "ng" or args[-1] == "alt":
            track = ' '.join(args[-2:])
            player = ' '.join(args[:-2])
        else:
            track = args[-1]
            player = ' '.join(args[:-1])

        track = self.DB.get_track_name(track.upper())
        if track is None:
            await msg.channel.send("Sorry, I don't know that track :disappointed:")
            return

        player_ids = self.DB.get_player_id(player)
        ghost_hash = ""
        time = ""
        if len(player_ids) == 0:
            await msg.channel.send("Sorry, I don't know that player :disappointed:")
            return
        elif len(player_ids) == 1:
            pb = self.DB.get_player_pb(player_ids[0][0], track[0])
            if pb is None:
                await msg.channel.send("I couldn't find a time for that track on CTGP-R.")
                return
            ghost_hash = pb[0]
            time = pb[1]
        else:
            # in case a player has more than 1 ID, figure out which one has the fastest time
            fastest = FinishTime("99:99.999")
            found_pb = False
            for player_id in player_ids:
                pb = self.DB.get_player_pb(player_id[0], track[0])
                print(pb)
                if pb is None:
                    continue
                else:
                    found_pb = True
                finish_time = FinishTime(pb[1])
                if finish_time.ms_total < fastest.ms_total:
                    fastest = finish_time
                    ghost_hash = pb[0]
            if not found_pb:
                await msg.channel.send("I couldn't find a time for that track on CTGP-R.")
                return
            time = str(fastest)

        ghost_link = "http://www.chadsoft.co.uk/time-trials/rkgd/{}/{}/{}.html".format(ghost_hash[:2], ghost_hash[2:4], ghost_hash[4:])

        player = player + "'" + (player[-1] != 's' and player[-1] != 'x') * "s"

        embed = discord.Embed(title="**{} personal best**".format(player), colour=0x8eff56)
        embed.add_field(name=track[0], value="[{}]({})".format(self.easter_egg(time), ghost_link))
        embed.set_thumbnail(url=self.extract_mii(ghost_link))

        await msg.channel.send(embed=embed)


    async def command_info(self, msg, command):
        """Provides info on a command"""

        message = ""
        if command == "help":
            await msg.channel.send(":thinking:")
        elif command == "tops":
            embed = discord.Embed(title="**!tops track category**", colour=0x990000)
            embed.add_field(name="track", value="track abbreviation, e.g.: `LC`, `rYF`", inline=False)
            embed.add_field(name="category", value="`ng` (no-glitch), `alt` (alternative).\n*Only add category if there is more than 1*", inline=False)
            await msg.channel.send(embed=embed)
        elif command == "links":
            await msg.channel.send(":expressionless: Just type `!links`")
        elif command == "count":
            embed = discord.Embed(title="**!count player**", colour=0x990000)
            embed.add_field(name="player", value="player name, e.g.: `Olifré`")
            await msg.channel.send(embed=embed)
        elif command == 'pb':
            embed = discord.Embed(title="**!pb player track**", colour=0x990000)
            embed.add_field(name="player", value="player name, e.g.: `Olifré`", inline=False)
            embed.add_field(name="track", value="track abbreviation, e.g.: `LC`, `rYF`", inline=False)
            await msg.channel.send(embed=embed)

    async def auto_update(self, loop_duration):
        """attempts to update the tops every (loop_duration) seconds"""

        await self.wait_until_ready()
        channel = self.get_channel(Config.CHANNEL)

        while not self.is_closed():
            await self.change_presence(activity=discord.Game(name="Checking Database"), status=discord.Status.idle)
            print("updating")
            times, changed = await self.bnl.update_tops(self.client)
            # times = [("Koopa Cape", Ghost('🇧🇪', "Olifré", "02:18.400", "http://www.chadsoft.co.uk/time-trials/rkgd/AF/6E/DBD745DB99D8853C2E21BB83AB13820A35BC.html"), 3)]
            # self.bnl.add_time(times[0][1], times[0][0])
            # print(times)
            self.last_updated = datetime.datetime.utcnow()
            print("finished updating")

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

        time_str = self.easter_egg(str(time.time))
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

    def easter_egg(self, time_str):
        """A little easter egg ;-)"""
        if time_str[-2:] == "69":
            time_str = time_str[:-2] + ":six::nine:"
        if time_str[-3:] == "420":
            time_str += " :fire::fire:"

        return time_str


if __name__ == "__main__":
    token = Config.TOKEN
    bot = Bot()
    bot.run(token)
