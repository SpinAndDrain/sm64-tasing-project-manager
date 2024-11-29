import json
import secret


def setup(context):
    @context.bot.command(hidden=True, aliases=["u"], brief="Configures the bot")
    async def update(ctx, label = None, kvpairs = None):
        if not context.is_privileged(ctx.author.id):
            return
        
        if label == "projects":
            if len(ctx.message.attachments) < 1:
                await ctx.send(":x: Missing attachement")
                return
            cont = await ctx.message.attachments[0].read()
            context.project_manager._data = json.loads(cont)
            context.project_manager.publish_changes()
            await ctx.send(":white_check_mark: This probably worked :stuck_out_tongue_winking_eye:")
            return
        
        if label == "settings":
            if not kvpairs:
                await ctx.send(":x: Missing kvpairs")
                return
            for e in kvpairs.split(";"):
                k, v = e.split("=")
                k = k.strip()
                v = v.strip()
                settings[k] = v
            secret.write_env_file("settings.env", settings)
            await ctx.send(":white_check_mark: This probably worked :stuck_out_tongue_winking_eye:")
            return
        
        await ctx.send(":x: Invalid syntax `!update <projects|settings> [<kvpairs>]`")
