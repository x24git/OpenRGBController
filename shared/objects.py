class UniqueSingleton(type):
    _instances = {}

    @classmethod
    def make_hash(mcs, *args, **kwargs):
        return hash(kwargs) + hash(args)

    def __call__(cls, *args, **kwargs):
        hash_cache = cls.make_hash(*args, **kwargs)
        if hash_cache not in cls._instances:
            cls._instances[hash_cache] = super(UniqueSingleton, cls).__call__(*args, **kwargs)
        else:
            print("instance of similar type already exists")
        return cls._instances[hash_cache]


class SessionExistsWarning(RuntimeWarning):
    def __init__(self, *args):
        super(SessionExistsWarning, self).__init__("An existing session for this handler exists. "
                                                   "Close the existing session before opening a new session.")
