import traffic


def setup(context):
    @context.bot.command(brief="Tests if the provided upload location is available")
    async def test(ctx, id_or_project: context.to_lower = None, stage: context.to_lower = None, star: context.to_lower = None):
        """
        Tests if the provided upload location is available. This can be used to validate if your TAS can be uploaded.

        Usages:
            !test <id>
            !test <project> <stage> <star>
        Arguments:
            id: An ID string describing the upload location. Format: <project>_<stage>-<star> (e.g. ama_4-2)
            project: The project of the upload location (e.g. ama)
            stage: The stage of the project of the upload location (e.g. 4)
            star: The star of the stage of the upload location (e.g. 2)
        """
        if not id_or_project:
            await ctx.send(f":x: Invalid syntax. Type `!help` for help.")
            return

        if not stage:
            a,b,c,d = traffic.unpack_id(id_or_project)
            id_or_project = a
            stage = b
            star = c
        
        if context.project_manager.has_star(id_or_project, stage, star):
            await ctx.send(f":white_check_mark: Upload location available")
        else:
            await ctx.send(f":x: Upload location not available. Use `!tree [<project>]` to get a list of available projects, stages and stars.")
