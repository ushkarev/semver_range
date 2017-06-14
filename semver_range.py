class Version:
    def __init__(self, version):
        self.version = version
        self.major = None
        self.minor = None
        self.patch = None
        self.pre_release = None
        self.build = None
        raise NotImplementedError

    def __str__(self):
        return self.version

    def __repr__(self):
        return '<Version %s>' % self


class Range:
    def __init__(self, pattern):
        self.pattern = pattern
        raise NotImplementedError

    def __str__(self):
        return self.pattern

    def __repr__(self):
        return '<Range %s>' % self

    def __contains__(self, version):
        if not isinstance(version, Version):
            version = Version(version)
        raise NotImplementedError
