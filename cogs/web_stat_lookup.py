import discord
import requests
from discord.ext import commands
from requests import JSONDecodeError

from resources import characters


class WebStatLookup(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="ostat", help="Look up player batting stats on Project Rio")
    async def o_stat(self, ctx, user="all", char="all"):
        url = "https://api.projectrio.app/detailed_stats/?exclude_pitching=1&exclude_fielding=1&exclude_misc=1&tag=Normal&tag=Ranked"
        all_url = url

        try:
            if char.lower() in characters.aliases:
                char = characters.mappings[characters.aliases[char.lower()]]
            if char != "all":
                url += "&char_id=" + str(characters.reverse_mappings[char])
                if user != "all":
                    all_url = url

            if user != "all":
                url += "&username=" + user

            all_response = requests.get(all_url).json()
            response = requests.get(url).json()

            stats = response["Stats"]["Batting"]
            pa = stats["summary_at_bats"] + stats["summary_walks_bb"] + stats["summary_walks_hbp"] + stats[
                "summary_sac_flys"]
            avg = stats["summary_hits"] / stats["summary_at_bats"]
            obp = (stats["summary_hits"] + stats["summary_walks_hbp"] + stats["summary_walks_bb"]) / pa
            slg = (stats["summary_singles"] + (stats["summary_doubles"] * 2) + (stats["summary_triples"] * 3) + (
                    stats["summary_homeruns"] * 4)) / stats["summary_at_bats"]
            ops = obp + slg
            # pa = stats["plate_appearances"]

            overall = all_response["Stats"]["Batting"]
            overall_pa = overall["summary_at_bats"] + overall["summary_walks_bb"] + overall["summary_walks_hbp"] + \
                         overall[
                             "summary_sac_flys"]
            overall_obp = (overall["summary_hits"] + overall["summary_walks_hbp"] + overall[
                "summary_walks_bb"]) / overall_pa
            overall_slg = (overall["summary_singles"] + (overall["summary_doubles"] * 2) + (
                    overall["summary_triples"] * 3) + (
                                   overall["summary_homeruns"] * 4)) / overall["summary_at_bats"]

            ops_plus = ((obp / overall_obp) + (slg / overall_slg) - 1) * 100

            c_o = " cOPS+"
            if char == "all" or user == "all":
                c_o = " OPS+"

            embed = discord.Embed(title=user + " - " + char + " (" + str(pa) + " PA)",
                                  description="AVG: " + "{:.3f}".format(avg) + "\nOBP: " + "{:.3f}".format(obp) +
                                              "\nSLG: " + "{:.3f}".format(slg) + "\nOPS: " + "{:.3f}".format(ops) +
                                              "\n" + c_o + ": " + str(round(ops_plus)))

            embed.set_thumbnail(url=characters.images[char])

            await ctx.send(embed=embed)
        except JSONDecodeError:
            await ctx.send("JSON Error")
        except KeyError:
            await ctx.send("Key Error")

    @commands.command(name="pstat", help="Look up player pitching stats on Project Rio")
    async def p_stat(self, ctx, user="all", char="all"):
        url = "https://api.projectrio.app/detailed_stats/?exclude_batting=1&exclude_fielding=1&exclude_misc=1&tag=Normal&tag=Ranked"
        all_url = url

        try:
            if char.lower() in characters.aliases:
                char = characters.mappings[characters.aliases[char.lower()]]
            if char != "all":
                url += "&char_id=" + str(characters.reverse_mappings[char])
                if user != "all":
                    all_url = url

            if user != "all":
                url += "&username=" + user

            all_response = requests.get(all_url).json()
            response = requests.get(url).json()

            stats = response["Stats"]["Pitching"]

            # batter avg vs pitcher
            d_avg = stats["hits_allowed"] / (stats["batters_faced"] - stats["walks_bb"] - stats["walks_hbp"])
            era = 9 * stats["runs_allowed"] / (stats["outs_pitched"] / 3)
            # strikeout percentage
            kp = (stats["strikeouts_pitched"] / stats["batters_faced"]) * 100

            ip = stats["outs_pitched"] // 3
            ip_str = str(ip + (0.1 * (stats["outs_pitched"] % 3)))

            overall = all_response["Stats"]["Pitching"]
            overall_era = 9 * overall["runs_allowed"] / (overall["outs_pitched"] / 3)
            # character ERA-
            cera_minus = (era / overall_era) * 100

            char_or_all = " cERA-"
            if char == "all" or user == "all":
                char_or_all = " ERA-"

            embed = discord.Embed(title=user + " - " + char + " (" + ip_str + " IP)",
                                  description="opp. AVG: " + "{:.3f}".format(d_avg) + "\nERA: " + "{:.2f}".format(era) +
                                              "\nK%: " + "{:.1f}".format(kp) + "\n" + char_or_all + ": " + str(round(cera_minus)))

            embed.set_thumbnail(url=characters.images[char])

            await ctx.send(embed=embed)
        except JSONDecodeError:
            await ctx.send("JSON Error")
        except KeyError:
            await ctx.send("Key Error")


async def setup(client):
    await client.add_cog(WebStatLookup(client))
