import traffic


def setup(context):
    @context.bot.command(brief="Retrieves the download URLs to a previous upload")
    async def url(ctx, id_or_project: context.to_lower = None, stage: context.to_lower = None, star: context.to_lower = None, time = None, key = None):
        """
        Retrieves the download URLs to a previous upload.

        Usages:
            !url <project> <stage> <star> <time>
            !url <id>

        Note: To retrieve URLs of miscellaneous TASes, the star character (*) can be passed as an argument for identification.
        Usages of misc uploads:
            !url <project> * <key>                   project-global misc TAS
            !url <project> <stage> * <key>           stage-global misc TAS
            !url <project> <stage> <star> * <key>    star-local misc TAS
        
        Arguments:
            project: The project to which the TAS belongs
            stage: The stage/course/level in which the TAS plays
            star: The star in the stage which the TAS collects
            time: The time of the TAS
            id: A compact ID string describing all of the arguments above this line. Format: <project>_<stage>-<star>.<time> (e.g. ama_4-2.867)
            key: A user-defined key under which a miscellaneous TAS is stored instead of a time

        """
        if not id_or_project:
            await ctx.send(f":x: Invalid syntax. Type `!help` for help.")
            return
        
        uloc = context.project_manager.construct_upload_location(id_or_project, stage, star, time, key)
        if isinstance(uloc, int):
            await ctx.send(f":x: Target location could not be determined (**{traffic.get_invalid_upload_location_reason(uloc)}**). Try `!help url` for help with the syntax or `!tree` for a list of available projects, stages and stars.")
            return

        if not context.validate_limits(ctx, 1):
            await ctx.send(f":x: Request limit reached")
            return

        s = ""
        m64_url, st_url = context.github_traffic.get_urls(uloc)
        if m64_url:
            s += f"M64: {m64_url}\n"
        if st_url:
            s += f"ST: {st_url}"

        if len(s) == 0:
            await ctx.send(":x: Could not retrieve download URLs for your target")
        else:
            await ctx.send(s)
