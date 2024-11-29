import traffic
import secret
import limits
import cache
import discord
from discord.ext import commands as cmds
from commands.command_context import CommandContext

from commands import *


def setup_bot(ENV):
    # setup
    intents = discord.Intents.default()
    intents.message_content = True
    bot = cmds.Bot(command_prefix='!', intents=intents, help_command=cmds.DefaultHelpCommand(no_category="Available Commands", show_parameter_descriptions=False))

    settings = secret.read_env_file("settings.env")
    gtraffic = traffic.Traffic(ENV["GHKEY"], settings)
    manager = traffic.ProjectManager()

    rftcache = cache.RftCache(settings['DISC_CACHE_STATE_PATH'], gtraffic)
    rftcache.integrate()

    def _is_privileged(user):
        return str(user) in settings["PRIVILEGED_USERS"].split(',')

    def _limit_validation(ctx, amount):
        if ghlimits.can_request_now(ctx.author.id, amount):
            ghlimits.acknowledge(ctx.author.id, amount)
            return True
        return False

    def to_lower(arg):
        return arg and arg.lower()
    
    ghlimits = limits.RequestLimiter(int(settings["GH_REQ_LIMIT"]), int(settings["GH_REQ_RECOVERY"]), _is_privileged)

    command_context = CommandContext(intents, bot, settings, gtraffic, ghlimits, manager, rftcache, to_lower, _is_privileged, _limit_validation)

    # checks
    @bot.check
    def _is_not_blacklisted(ctx):
        return str(ctx.author.id) not in settings["BANNED_USERS"].split(',')

    # functions
    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        print('------')
    
    commands = [delete, get, listfiles, test, tree, update, upload, url]

    for command in commands:
        command.setup(command_context)

    return bot