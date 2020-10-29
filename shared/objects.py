class UniqueSingleton(type):
    _instances = {}

    @classmethod
    def make_hash(mcs, *args, **kwargs):
        return hash(frozenset(kwargs)) + hash(args)

    def __call__(cls, *args, **kwargs):
        hash_cache = cls.make_hash(*args, **kwargs)
        if hash_cache not in cls._instances:
            cls._instances[hash_cache] = super(UniqueSingleton, cls).__call__(*args, **kwargs)
        else:
            print("instance of similar type already exists")
        return cls._instances[hash_cache]


class SessionRedefinitionWarning(RuntimeWarning):
    pass


class SessionTimeout(TimeoutError):
    pass


class SessionLost(ConnectionResetError):
    pass


class SessionOffline(ConnectionRefusedError):
    pass

