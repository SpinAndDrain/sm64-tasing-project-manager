import fileget
import traffic


def setup(context):
    @context.bot.command(brief="Uploads a TAS", aliases=["ul"])
    async def upload(ctx,
            url1_or_id_or_project = None,
            url2_or_stage = None,
            id_or_poject_or_star = None,
            stage_or_time = None,
            star_or_key = None,
            time = None,
            key = None
            ):
        """
        Uploads a TAS. The bot responds with two download URLs describing the storage locations of the M64 and ST files.
        The target M64 and ST files can either be attached to the message executing the command or provided as URLs via the arguments.
        This operation can fail if there was already a TAS uploaded with the same time or key.
        If no arguments are provided, the bot will try to guess the store location based on the filename of the M64 file.

        Aliases: !ul
        Usages:
            !upload [<m64-url>] [<st-url>] <project> <stage> <star> <time>
            !upload [<m64-url>] [<st-url>] <id>
            !upload [<m64-url>] [<st-url>]

        Note: To upload miscellaneous TASes that do not match a specific single star run of a project, the star character (*) can be passed as an argument to save the TAS elsewhere. The TAS is then stored under a user-defined key rather than a time.
        Usages of misc uploads:
            !upload <project> * <key>                   project-global misc TAS
            !upload <project> <stage> * <key>           stage-global misc TAS
            !upload <project> <stage> <star> * <key>    star-local misc TAS

        Arguments:
            m64-url: The url to the M64 file of your TAS if you do not provide it as an attachment
            st-url: The url to the ST file of your TAS if you do not provide it as an attachment
            project: The project to which the TAS belongs
            stage: The stage/course/level in which the TAS plays
            star: The star in the stage which the TAS collects
            time: The time of the TAS
            id: A compact ID string describing all of the arguments above this line. Format: <project>_<stage>-<star>.<time> (e.g. ama_4-2.867)
            key: A user-defined key under which a miscellaneous TAS is stored instead of a time

        """
        m64 = None
        st = None

        for a in ctx.message.attachments:
            if not m64 and a.filename.endswith(".m64"):
                m64 = a
            if not st and (a.filename.endswith(".st") or a.filename.endswith(".savestate")):
                st = a

        #read urls from arguments for two files max
        for _ in range(2):
            if fileget.is_url(url1_or_id_or_project):
                rf = fileget.RemoteFile(url1_or_id_or_project)
                _, ext = rf.get_file_info()
                if not m64 and ext == "m64":
                    m64 = rf
                elif not st and (ext == "st" or ext == "savestate"):
                    st = rf
                url1_or_id_or_project, url2_or_stage, id_or_poject_or_star, stage_or_time, star_or_key, time = url2_or_stage, id_or_poject_or_star, stage_or_time, star_or_key, time, key
            else:
                break

        #if not m64 or not st:
        if not m64:
            await ctx.send(f":x: Missing file(s). To upload a TAS, you must provide an M64 and optionally an ST file, each as either an attachment or a URL.")
            return
        
        #file size limit check
        m64_size = m64.size if hasattr(m64, 'size') else m64.get_file_size()
        if m64_size <= 0 or m64_size > int(context.settings["M64_FILE_SIZE_LIMIT"]):
            await ctx.send(f":x: The provided M64 file is either invalid or exceeds the file size limit.")
            return
        
        # only check if provided
        if st:
            st_size = st.size if hasattr(st, 'size') else st.get_file_size()
            if st_size <= 0 or st_size > int(context.settings["ST_FILE_SIZE_LIMIT"]):
                await ctx.send(f":x: The provided ST file is either invalid or exceeds the file size limit.")
                return

        if not url1_or_id_or_project:
            file_name, file_extension = m64.filename.rsplit(".", 1) if hasattr(m64, 'filename') else m64.get_file_info()
            url1_or_id_or_project = file_name

        url1_or_id_or_project = url1_or_id_or_project.lower()                           #either id or project
        url2_or_stage = url2_or_stage and url2_or_stage.lower()                         #either nothing or stage
        id_or_poject_or_star = id_or_poject_or_star and id_or_poject_or_star.lower()    #either nothing or star

        uloc = context.project_manager.construct_upload_location(url1_or_id_or_project, url2_or_stage, id_or_poject_or_star, stage_or_time, star_or_key)
        if isinstance(uloc, int):
            await ctx.send(f":x: The upload location could not be determined (**{traffic.get_invalid_upload_location_reason(uloc)}**). Try `!help upload` for help with the syntax or `!tree` for a list of available projects, stages and stars.")
            return

        if context.rft_cache.get_element(uloc):
            await ctx.send(f":x: A TAS with your specified time or key was already uploaded at the target location. Please make sure you have provided the correct time or key, or try uploading your TAS as \"miscellaneous\" (`!help upload`).")
            return

        if not context.validate_limits(ctx, 2 if st else 1):
            await ctx.send(f":x: Request limit reached")
            return

        author = f"{ctx.author.name}/{ctx.author.id}"
        m64_content = await m64.read() if hasattr(m64, 'read') else m64.download()
        m64_url = context.github_traffic.upload(f"{uloc}/{m64.filename if hasattr(m64, 'filename') else '.'.join(m64.get_file_info())}", author, m64_content, context.rft_cache)
        st_url = None
        if st and m64_url:
            st_content = await st.read() if hasattr(st, 'read') else st.download()
            st_url = context.github_traffic.upload(f"{uloc}/{st.filename if hasattr(st, 'filename') else '.'.join(st.get_file_info())}", author, st_content, context.rft_cache)

        if not m64_url or (not st_url and st):
            await ctx.send(f":x: Upload failed")
            return

        str_to_send = f":white_check_mark: Upload successful\nM64: {m64_url}"
        if st_url:
            str_to_send += f"\nST: {st_url}"
        await ctx.send(str_to_send)
