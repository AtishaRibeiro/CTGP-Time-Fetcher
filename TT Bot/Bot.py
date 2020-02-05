import discord
import Config
import asyncio
# import datetime not needed?
import aiohttp
import urllib
import logging
from bs4 import BeautifulSoup as BS
from DB import DB
from TopsUpdater import Tops, ImprovementType
from API_Querier import Ghost, FinishTime


COMMAND_PREFIX = '!'

class Bot(discord.Client):
    """Bot that handles the BNL Tops and more"""

    def __init__(self):
        super().__init__()

        self.DB = DB("tt_bot_db.db")
        self.bg_task = self.loop.create_task(self.auto_update(3600))
        self.player_update_timer = 0
        self.client = aiohttp.ClientSession()
        self.tops = Tops(self.DB, self.client)
        # True if auto_update has to show all times, False if it only has to show top10 times
        self.show_all = True

        logging.basicConfig(filename="bot_log.log",
                            filemode='a',
                            format="+++++++++++++++++++++++++++++++++++++++\n"\
                            "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.ERROR)

        logging.info("Runing Bot")

        self.logger = logging.getLogger('Bot')
    
    async def on_ready(self):
        print("logged in")
        pass

    async def on_message(self, msg):
        """analyze all messages sent"""

        if msg.author == self.user:
            return

        admin = self.check_role(msg)

        if msg.channel.id == Config.DMCHANNEL:
            admin = True
            if msg.content[0] != COMMAND_PREFIX:
                await self.get_channel(Config.CHANNEL).send(f"```{msg.content}```")
                return
        elif msg.channel.id != Config.CHANNEL:
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
                    await self.get_tops(msg, split_msg[1])
                elif command == "count":
                    await self.count(msg, split_msg[1])
                elif command == "pb":
                    await self.pb(msg, split_msg[1].split())
                elif admin:
                    if command == "show_all":
                        await self.set_show_all(msg, split_msg[1])
                    elif command == "set_name":
                        await self.set_name(msg, split_msg[1].split())
                    elif command == "set_player":
                        await self.set_player(msg, split_msg[1].split())
                    elif command == "remove_player":
                        await self.remove_player(msg, split_msg[1])
                    elif command == "reset_track":
                        await self.reset_track(msg, split_msg[1])
                    elif command == "remove_time":
                        await self.remove_time(msg, split_msg[1])

            elif command == "help":
                await self.help(msg)
            elif command == "links":
                await self.links(msg)
            elif admin:
                if command == "reset":
                    await self.reset(msg)
                elif command == "cancel":
                    await self.cancel(msg)
                elif command == "test":
                    await self.test(msg)
        else:
            return

    def check_role(self, msg):
        try:
            for role in msg.author.roles:
                if role >= msg.guild.get_role(Config.MODERATOR):
                    return True
        except (TypeError, AttributeError) as e:
            return False
        return False

    async def reset(self, msg):
        self.bg_task.cancel()
        self.bg_task = self.loop.create_task(self.auto_update(3600))
        await msg.channel.send("`reset`")

    async def cancel(self, msg):
        self.bg_task.cancel()
        self.bg_task = self.loop.create_task(self.auto_update(3600, False))
        await msg.channel.send("`cancelled`")

    async def set_show_all(self, msg, arg):
        if arg == "true":
            self.show_all = True
            await msg.channel.send("Set `show_all` to True")
        elif arg == "false":
            self.show_all = False
            await msg.channel.send("Set `show_all` to False")

    async def set_name(self, msg, args):
        if self.DB.set_player_name(args[0], args[1]):
            await msg.channel.send("`Name set`")
        else:
            await msg.channel.send("`Unknown player`")

    async def set_player(self, msg, args):
        print(args[0], args[1], args[2])
        self.DB.set_player(args[0], args[1], args[2])
        await msg.channel.send("`player set`")

    async def remove_player(self, msg, player_id):
        if self.DB.remove_player(player_id):
            await msg.channel.send("`player removed`")
        else:
            await msg.channel.send("`player doesn't exist`")

    async def reset_track(self, msg, track):
        full_track = self.DB.get_track_name(track.upper())[0]
        times = self.DB.reset_track(full_track)
        for time in times:
            self.tops.add_time(Ghost(time[0], time[1], time[2], self.get_ghost_link(time[3])), full_track)
        await msg.channel.send(f"`reset {full_track}`")

    async def remove_time(self, msg, ghost_hash):
        self.DB.ban_time(ghost_hash)
        await msg.channel.send("`removed`")

    async def get_tops(self, msg, args):
        """tops command"""

        if args.lower() == "all":
            author = msg.author
            dm_channel = author.dm_channel
            if dm_channel is None:
                await author.create_dm()
                dm_channel = author.dm_channel

            await self.create_tops_dm_embeds(dm_channel, self.DB.get_all_tops())
            return

        try:
            full_track = self.DB.get_track_name(args.upper())[0]
            tops = self.tops.get_top_10(full_track)
            await msg.channel.send(embed=self.create_tops_embed(full_track, tops))
        except (IndexError, TypeError):
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
                    "- [TAS WR's](http://mkwtas.com/) all current TAS world records"

        embed.add_field(name="\u200B", value=message)
        await msg.channel.send(embed=embed)

    async def count(self, msg, player):
        """provides the amount of times a player appears in the leaderboards"""

        embed = discord.Embed(title="**BNL Leaderboard appearances**", colour=0xffffff)
        player_name, total_count, ng_count, glitch_count, alt_count = self.DB.get_player_count(player)
        if player_name is None:
            player_name = player

        message = "**{}/32** *no-glitch*\n**{}/14** *glitch*\n**{}/2** *alternate*".format(ng_count, glitch_count, alt_count)

        embed.add_field(name="`{}` appears **{}** time(s) in the leaderboards".format(player_name, total_count), value=message)
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
        player_name = ""
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
            player_name = pb[0]
            ghost_hash = pb[1]
            time = pb[2]
        else:
            # in case a player has more than 1 ID, figure out which one has the fastest time
            fastest = FinishTime("99:99.999")
            found_pb = False
            for player_id in player_ids:
                pb = self.DB.get_player_pb(player_id[0], track[0])
                if pb is None:
                    continue
                else:
                    found_pb = True
                finish_time = FinishTime(pb[2])
                if finish_time.ms_total < fastest.ms_total:
                    fastest = finish_time
                    player_name = pb[0]
                    ghost_hash = pb[1]
            if not found_pb:
                await msg.channel.send("I couldn't find a time for that track on CTGP-R.")
                return
            time = str(fastest)

        ghost_link = self.get_ghost_link(ghost_hash)

        player_name = player_name + "'" + (player_name[-1] != 's' and player_name[-1] != 'x') * "s"

        embed = discord.Embed(title="**{} personal best**".format(player_name), colour=0x8eff56)
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

    async def auto_update(self, loop_duration, start_immediately=True):
        """attempts to update the tops every (loop_duration) seconds"""

        try:
            await self.wait_until_ready()
            channel = self.get_channel(Config.UPDATE_CHANNEL)

            while not self.is_closed():
                if start_immediately:
                    await self.change_presence(activity=discord.Game(name="Checking Database"), status=discord.Status.idle)

                    if self.player_update_timer == 0:
                        await self.tops.update_players()
                        self.player_update_timer = 20
                    else:
                        self.player_update_timer -= 1

                    try:
                        print("updating")
                        times, changed = await self.tops.update_tops(self.client)
                        print("finished updating", flush=True)

                        for time_info in times:
                            if not self.show_all and time_info[2] == ImprovementType.none:
                                continue
                            await channel.send(embed=(self.create_update_embed(time_info)))
                    except Exception as e:
                        logging.exception("Exception occurred")

                await self.change_presence(activity=None, status=discord.Status.online)
                start_immediately = True
                await asyncio.sleep(loop_duration)

        except Exception as e:
            logging.critical("Exception occurred", exc_info=True)

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

    async def create_tops_dm_embeds(self, dm_channel, cups):
        """formats embeds for dm message"""

        for cup in cups:
            embed = discord.Embed(title=cup, colour=0x333333)

            for track in cups[cup]:
                message = ""
                tops = self.tops.get_top_10_no_db(track[1])
                for pos, time in tops:
                    pos_str = str(pos)
                    if len(pos_str) == 1:
                        #alignment
                        pos_str = '\u200B ' + pos_str
                    message += "{}. {} {}: {}\n".format(pos_str, time.country, time.name, time.time)
                if len(message) == 0:
                    message = "empty tops"

                embed.add_field(name=track[0], value=message, inline=True)
                
            await dm_channel.send(embed=embed)

    def create_update_embed(self, time_info):
        """formats the update message"""

        time = time_info[1]

        medals = {1: "🥇", 2: "🥈", 3: "🥉", 4:""}

        title = "{} ".format(time.name)
        improvement_type = time_info[2].value
        if improvement_type == 0 or improvement_type == 1:
            title += "improved their time! Keep it up, proud of you"
        elif improvement_type == 2:
            title += "enters the top 10! Welcome!"
        elif improvement_type == 3:
            title += "claims first place! All hail the new king"
        elif improvement_type == 4:
            title += "ties for 1st place! What are the chances?"
        elif improvement_type == 5:
            title += "improved their BNL record!"

        field_title = "*{}*".format(time_info[0])

        time_str = self.easter_egg(str(time.time))
        message = "{} {}: [{}]({}) {}\n".format(time.country, time.name, time_str, time.ghost, medals[time_info[3]])

        colour = 0x8eff56
        # make the embed colour yellow if it's a top10 time
        if improvement_type != 0:
            colour = 0xffcc00

        embed = discord.Embed(title=title, colour=colour)
        embed.add_field(name=field_title, value=message)
        embed.set_thumbnail(url=self.extract_mii(time.ghost))
        return embed

    def get_ghost_link(self, ghost_hash):
        return "http://www.chadsoft.co.uk/time-trials/rkgd/{}/{}/{}.html".format(ghost_hash[:2], ghost_hash[2:4], ghost_hash[4:])

    def extract_mii(self, link):
        """Extracts the url to the mii image file"""

        try:
            html = urllib.request.urlopen(link)
            soup = BS(html, features="html5lib")
            parent_div = soup.findAll("div", class_="_1c5")[0]
            child_div = parent_div.contents[1]
            div_str = str(child_div)

            start = div_str.find("url('") + 5
            end = div_str.find("')", start)
            mii = div_str[start:end]

            return "http://www.chadsoft.co.uk" + mii
        except urllib.error.HTTPError:
            return ""
        except urllib.error.URLError:
            return ""

    def easter_egg(self, time_str):
        """A little easter egg ;-)"""
        if time_str[-2:] == "69":
            time_str = time_str[:-2] + "6️⃣9️⃣"
        if time_str[-3:] == "420":
            time_str += " 🔥🔥"
        if time_str[-3:] == "666":
            time_str += " 😈"
        if time_str[-3:] == "777":
            time_str = time_str[:-3] + "🎰"

        return time_str

    async def test(self, msg):
        """For testing purposes"""
        result = self.tops.add_time(Ghost('🇧🇪', "Olifré", "01:09.000", "http://www.chadsoft.co.uk/time-trials/rkgd/E4/7B/97C4E27C6AA1A5ECC33DF5F70501CD33F92.html"), "Luigi Circuit")
        print(result)


if __name__ == "__main__":
    token = Config.TOKEN
    bot = Bot()
    bot.run(token)
