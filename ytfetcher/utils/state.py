class RuntimeConfig:
    """
    Singleton to hold global runtime configuration.
    Defaults to 'Library Mode' (Silent/No Progress).
    """
    _verbose = False

    @classmethod
    def enable_verbose(cls):
        cls._verbose = True

    @classmethod
    def disable_verbose(cls):
        cls._verbose = False

    @classmethod
    def is_verbose(cls) -> bool:
        return cls._verbose

def should_disable_progress() -> bool:
    return not RuntimeConfig.is_verbose()