import discord


def setup(context):
    @context.bot.command(hidden=True, aliases=["g"], brief="Retrieves info about the bot's state")
    async def get(ctx, label = None):
        if not context.is_privileged(ctx.author.id):
            return
        
        f = None
        if label == "projects":
            f = "projects.json"
        elif label == "settings":
            f = "settings.env"
        elif label == "cache":
            f = context.settings['DISC_CACHE_STATE_PATH']
        else:
            await ctx.send(":x: Invalid syntax `!get <projects|settings>`")
            return

        with open(f, 'rb') as file:
            f = discord.File(file)
        
        await ctx.send(file=f)
