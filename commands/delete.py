import traffic


def get_author_from_cache(cache_entry):
    try:
        return int(next(iter(cache_entry.values())))
    except:
        return None


def setup(context):
    @context.bot.command(brief="Deletes a TAS", aliases=["del"])
    async def delete(ctx, url_or_id_or_project = None, stage: context.to_lower = None, star: context.to_lower = None, time = None, key = None):
        """
        Deletes a TAS. This action can only be performed by the author who previously uploaded the TAS.
        
        Aliases: !del
        Usages:
            !delete <url>
            !delete <id>
            !delete <project> <stage> <star> <time>
        
        Note: To delete miscellaneous TASes, the star character (*) can be passed as an argument for identification.
        Usages of misc uploads:
            !delete <project> * <key>                   delete project-global misc TAS
            !delete <project> <stage> * <key>           delete stage-global misc TAS
            !delete <project> <stage> <star> * <key>    delete star-local misc TAS

        Arguments:
            url: A URL to the TAS to be deleted
            project: The project to which the TAS belongs
            stage: The stage/course/level in which the TAS plays
            star: The star in the stage which the TAS collects
            time: The time of the TAS
            id: A compact ID string describing all of the arguments above this line. Format: <project>_<stage>-<star>.<time> (e.g. ama_4-2.867)
            key: A user-defined key under which a miscellaneous TAS is stored instead of a time

        """
        if not url_or_id_or_project:
            await ctx.send(f":x: Invalid syntax. Type `!help` for help.")
            return

        uloc = None
        TRAFFIC_REPOSITORY_URL_START = context.settings["TRAFFIC_REPOSITORY_URL_START"]
        if url_or_id_or_project.startswith(TRAFFIC_REPOSITORY_URL_START):
            uloc = url_or_id_or_project[len(TRAFFIC_REPOSITORY_URL_START):]
            if uloc.startswith("main/"):
                uloc = uloc[5:]
            if uloc.rfind(".") > uloc.rfind("/"):
                uloc = uloc[:uloc.rfind("/")]
            if uloc.endswith("/"):
                uloc = uloc[:-1]
        else:
            uloc = context.project_manager.construct_upload_location(url_or_id_or_project.lower(), stage, star, time, key)

        if isinstance(uloc, int) or len(uloc.strip()) == 0:
            await ctx.send(f":x: Target location could not be determined (**{traffic.get_invalid_upload_location_reason(uloc)}**). Try `!help delete` for help with the syntax or `!tree` for a list of available projects, stages and stars.")
            return

        if not context.rft_cache.get_element(uloc):
            await ctx.send(f":x: Your target TAS upload could not be found. Please make sure your arguments are correct (`!help delete`).")
            return

        if not context.is_privileged(ctx.author.id) and (get_author_from_cache(context.rft_cache.get_element(uloc)) != ctx.author.id):
            await ctx.send(f":x: Deletion failed. You are not the author.")
            return

        if not context.validate_limits(ctx, 3):
            await ctx.send(f":x: Request limit reached")
            return

        success, deletions = context.github_traffic.delete(uloc, f"{ctx.author.name}/{ctx.author.id}", context.rft_cache)
        if success:
            await ctx.send(f":white_check_mark: Successfully deleted {deletions} files")
        else:
            extra = ""
            if deletions > 0:
                extra = f" ({deletions} {'files were' if deletions > 1 else 'file was'} successfully deleted before this error occurred)"
            await ctx.send(f":x: Deletion failed{extra}")
