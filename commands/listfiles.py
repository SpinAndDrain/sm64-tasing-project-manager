import cache
#import re


def setup(context):
    @context.bot.command(brief="Lists all files of the given location in the remote repository", aliases=["lf"])
    async def listfiles(ctx, path = ""):
        """
        Lists all files of the given location in the remote repository. The location to be inspected is specified by the 'path' parameter.
        If this parameter is not specified, the contents of the root directory are listed.

        Aliases: !lf
        Usage: !listfiles [<path>]
        Arguments:
            path: If provided, lists the contents of the specified path in the remote repository, otherwise lists the contents of the root directory.
        """
        #normalized_path = path.strip()
        #normalized_path = re.sub(r'\s+', '', normalized_path)
        #normalized_path = re.sub(r'/{2,}', '/', normalized_path)
        #
        #current_dir = context.rft_cache.get_element(normalized_path)

        normalized_path = "/"
        current_dir = context.rft_cache.get_root()
        it = cache.NormalIteratorThatEveryAverageProgrammingLanguageHas(path.strip().split('/'))
        while it.has_next():
            nxt = it.next()
            if not nxt:
                # ignore empty path segment
                continue
            if (not isinstance(current_dir, dict)) or (nxt not in current_dir):
                await ctx.send(f":x: Invalid path segment `{nxt}` does not exist in `{normalized_path}`.")
                return
            current_dir = current_dir[nxt]
            normalized_path += f"/{nxt}"

        # in case we ended up at a file
        if not isinstance(current_dir, dict):
            await ctx.send(f":white_check_mark: File `{normalized_path}` exists.")
            return

        out = f"Contents of {normalized_path}:\n"
        for k, v in current_dir.items():
            out += f"\u2022 [{'d' if isinstance(v, dict) else 'f'}] {k}\n"

        await ctx.send(f"```{out}```")
