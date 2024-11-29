

class CommandContext:
    def __init__(self, intents, bot, settings, github_traffic, github_limits, project_manager, rft_cache, to_lower: callable, is_privileged: callable, validate_limits: callable):
        self._intents = intents
        self._bot = bot
        self._settings = settings
        self._github_traffic = github_traffic
        self._github_limits = github_limits
        self._project_manager = project_manager
        self._rft_cache = rft_cache
        self.to_lower = to_lower
        self.is_privileged = is_privileged
        self.validate_limits = validate_limits
    
    @property
    def intents(self):
        return self._intents
    
    @property
    def bot(self):
        return self._bot

    @property
    def settings(self):
        return self._settings

    @property
    def github_traffic(self):
        return self._github_traffic

    @property
    def github_limits(self):
        return self._github_limits

    @property
    def project_manager(self):
        return self._project_manager

    @property
    def rft_cache(self):
        return self._rft_cache
