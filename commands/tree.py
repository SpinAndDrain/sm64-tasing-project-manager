

def setup(context):
    @context.bot.command(brief="Lists available projects, stages and stars")
    async def tree(ctx, project: context.to_lower = None):
        """
        Lists available projects, stages and stars. If you don't specify the project parameter, this will list all available projects.
        If you specify the project parameter, this will list all stages and stars of that project.

        Usage: !tree [<project>]
        Arguments:
          project: If provided, lists all stages and stars of the project, otherwise lists all available projects.
        """

        tree = context.project_manager.tree(project)

        if isinstance(tree, str):
            await ctx.send(f"{tree}. Type !tree to get a list of available projects.")
            return

        name = context.project_manager.get_full_project_name(project)
        s = f"Structure of {name}:\n" if name else "Available projects:\n"
        maxkeylen = tree.pop() if isinstance(tree[-1], int) else None

        for e in tree:
            if maxkeylen:
                a,b = e.split(":")
                a = a.strip() + ":"
                b = b.strip()
                s += f"\u2022 {a.ljust(maxkeylen+2)}{b}\n"
            else:
                s += f"\u2022 {e}\n"

        if not project:
            s += "\nType !tree <project> to view the structure of a project."

        await ctx.send(f"```{s}```")
