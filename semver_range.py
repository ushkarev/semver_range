import functools
import itertools
import re


def parse_int(name, value, loose=False):
    if not loose and value.startswith('0') and value != '0':
        raise ValueError('%s has leading zeros' % name)
    value = int(value)
    if value < 0:
        raise ValueError('%s is not a natural number' % name)
    return value


def compare_identifiers(a, b, comparator='__eq__'):
    if not a and b:
        return comparator in ('__gt__', '__ge__')
    if a and not b:
        return comparator in ('__lt__', '__le__')
    a_converted = tuple(int(i) if i.isdigit() else i for i in a)
    b_converted = tuple(int(i) if i.isdigit() else i for i in b)
    try:
        return getattr(a_converted, comparator)(b_converted)
    except TypeError:
        return getattr(a, comparator)(b)


@functools.total_ordering  # for stable sorting of versions
class Version:
    """
    Implements Semantic Versioning 2.0.0
    http://semver.org/spec/v2.0.0.html
    """

    @classmethod
    def from_parts(cls, *parts):
        if len(parts) == 3:
            return cls('%s.%s.%s' % parts)
        if len(parts) == 4:
            return cls('%s.%s.%s-%s' % parts)
        if len(parts) == 5:
            if parts[3] is None and parts[4] is None:
                return cls('%s.%s.%s' % parts[:3])
            if parts[4] is None:
                return cls('%s.%s.%s-%s' % parts[:4])
            if parts[3] is None:
                return cls('{0}.{1}.{2}+{4}'.format(*parts))
            return cls('%s.%s.%s-%s+%s' % parts)
        raise ValueError('Invalid version')

    def __init__(self, version, loose=False):
        self.version = version
        self.loose = loose
        self.major = None
        self.minor = None
        self.patch = None
        self.pre_release = None
        self.build = None
        self._parse()

    def _parse(self):
        v = self.version
        if not isinstance(v, str):
            raise ValueError('Invalid version %r' % v)
        if not v:
            raise ValueError('Empty version')
        if self.loose:
            v = v.lstrip()
            if v[0] in ('v', '='):
                v = v[1:].lstrip()
        matches = re.match(r'^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<etc>.*)$', v)
        if not matches:
            raise ValueError('%s does not contain numeric major, minor and patch versions' % self.version)
        self.major = parse_int('major', matches.group('major'), loose=self.loose)
        self.minor = parse_int('minor', matches.group('minor'), loose=self.loose)
        self.patch = parse_int('patch', matches.group('patch'), loose=self.loose)

        etc = matches.group('etc')  # type: str
        if not etc:
            return
        self._parse_etc(etc)

    def _parse_etc(self, etc):
        identifier = re.compile(r'^[0-9A-Za-z-]+$')
        invalid_numeric_identifier = re.compile(r'^0\d+$')
        if self.loose and not etc.startswith('-') and not etc.startswith('+'):
            etc = '-' + etc
        if etc.startswith('-'):
            etc = etc[1:]
            if '+' in etc:
                pos = etc.index('+')
                self.pre_release, etc = etc[:pos], etc[pos:]
            else:
                self.pre_release, etc = etc, ''
            if not self.pre_release or \
                    not all(identifier.match(part) for part in self.pre_release_identifiers) or \
                    (not self.loose and any(
                        invalid_numeric_identifier.match(part) for part in self.pre_release_identifiers
                    )):
                raise ValueError('pre-release version %s is invalid in %s' % (self.pre_release, self.version))
        if etc.startswith('+'):
            self.build = etc[1:]
            if not self.build or not all(identifier.match(part) for part in self.build_identifiers):
                raise ValueError('build version %s is invalid in %s' % (self.build, self.version))
        elif etc:
            raise ValueError('Invalid version %s' % self.version)

    def __str__(self):
        if self.pre_release and self.build:
            return '%d.%d.%d-%s+%s' % (self.major, self.minor, self.patch, self.pre_release, self.build)
        if self.pre_release:
            return '%d.%d.%d-%s' % (self.major, self.minor, self.patch, self.pre_release)
        if self.build:
            return '%d.%d.%d+%s' % (self.major, self.minor, self.patch, self.build)
        return '%d.%d.%d' % (self.major, self.minor, self.patch)

    def __repr__(self):
        return '<Version "%s">' % self

    @property
    def is_stable(self):
        return self.major > 0

    @property
    def pre_release_identifiers(self):
        return self.pre_release.split('.') if self.pre_release else []

    @property
    def build_identifiers(self):
        return self.build.split('.') if self.build else []

    def increment(self, level):
        if level == 'major':
            return self.increment_major()
        if level == 'minor':
            return self.increment_minor()
        if level == 'patch':
            return self.increment_patch()
        if level == 'premajor':
            return self.increment_premajor()
        if level == 'preminor':
            return self.increment_preminor()
        if level == 'prepatch' or (not self.pre_release and level == 'prerelease'):
            return self.increment_prepatch()
        if level == 'prerelease':
            return self.increment_prerelease()
        raise ValueError('Unknown level %s' % level)

    def increment_major(self):
        if self.pre_release and self.patch == 0:
            # TODO: check pre-release incrementing
            return self.from_parts(self.major, self.minor, self.patch)
        return self.from_parts(self.major + 1, 0, 0)

    def increment_minor(self):
        if self.pre_release and self.patch == 0:
            # TODO: check pre-release incrementing
            return self.from_parts(self.major, self.minor, self.patch)
        return self.from_parts(self.major, self.minor + 1, 0)

    def increment_patch(self):
        if self.pre_release:
            return self.from_parts(self.major, self.minor, self.patch)
        return self.from_parts(self.major, self.minor, self.patch + 1)

    def increment_premajor(self):
        return self.from_parts(self.major + 1, 0, 0, 0)

    def increment_preminor(self):
        return self.from_parts(self.major, self.minor + 1, 0, 0)

    def increment_prepatch(self):
        return self.from_parts(self.major, self.minor, self.patch + 1, 0)

    def increment_prerelease(self):
        if not self.pre_release:
            return self.increment_prepatch()
        pre = self.pre_release_identifiers
        found_numeric = False
        for i in range(len(pre) - 1, -1, -1):
            if pre[i].isdigit():
                pre[i] = str(int(pre[i]) + 1)
                found_numeric = True
                break
        if not found_numeric:
            pre.append('0')
        return self.from_parts(self.major, self.minor, self.patch, '.'.join(pre))

    def to_parts(self):
        return self.major, self.minor, self.patch, self.pre_release, self.build

    @property
    def without_build(self):
        return self.from_parts(*self.to_parts()[:-1])

    def __hash__(self):
        return hash(str(self))

    def __copy__(self):
        return self.__class__(str(self), loose=self.loose)

    def __eq__(self, other):
        """
        Strict equality considers pre_release and build versions
        """
        cls = type(self)
        if isinstance(other, str):
            other = cls(other, loose=self.loose)
        elif not isinstance(other, cls):
            raise TypeError('%r is not a version' % other)
        self_short = self.to_parts()[:3]
        other_short = other.to_parts()[:3]
        return self_short == other_short and \
            compare_identifiers(self.pre_release_identifiers, other.pre_release_identifiers) and \
            compare_identifiers(self.build_identifiers, other.build_identifiers)

    def __lt__(self, other):
        """
        Strict ordering considers pre_release and build versions
        """
        cls = type(self)
        if isinstance(other, str):
            other = cls(other, loose=self.loose)
        elif not isinstance(other, cls):
            raise TypeError('%r is not a version' % other)
        self_short = self.to_parts()[:3]
        other_short = other.to_parts()[:3]
        if self_short < other_short:
            return True

        if self_short == other_short:
            if compare_identifiers(self.pre_release_identifiers, other.pre_release_identifiers, '__lt__'):
                return True
            if compare_identifiers(self.pre_release_identifiers, other.pre_release_identifiers):
                return compare_identifiers(self.build_identifiers, other.build_identifiers, '__lt__')
        return False

    def has_same_precedence(self, other):
        """
        A looser form of __eq__, build version is ignored and different pre_release versions are considered equal
        """
        cls = type(self)
        if isinstance(other, str):
            other = cls(other, loose=self.loose)
        elif not isinstance(other, cls):
            raise TypeError('%r is not a version' % other)
        self_short = self.to_parts()[:3]
        other_short = other.to_parts()[:3]
        if self_short != other_short:
            return False
        return (not self.pre_release and not other.pre_release) or (self.pre_release and other.pre_release)

    def precedes(self, other):
        """
        A looser form of __lt__, build version is ignored and different pre_release versions are considered equal
        """
        cls = type(self)
        if isinstance(other, str):
            other = cls(other, loose=self.loose)
        elif not isinstance(other, cls):
            raise TypeError('%r is not a version' % other)
        self_short = self.to_parts()[:3]
        other_short = other.to_parts()[:3]
        if self_short < other_short:
            return True
        if self_short == other_short:
            return self.pre_release and not other.pre_release
        return False


class Range:
    """
    Implements npm-style semantic version matching
    https://docs.npmjs.com/misc/semver
    """
    identifier = r'[0-9A-Za-z-]+'
    identifiers = r'%s(\.%s)*' % (identifier, identifier)
    part = r'(\d+|x|X|\*)'
    partial = r'%s+(\.%s(\.%s(\-%s)?(\+%s)?)?)?' % (part, part, part, identifiers, identifiers)
    partial_loose = r'v?\s*%s+(\.%s(\.%s(\-?%s)?(\+%s)?)?)?' % (part, part, part, identifiers, identifiers)

    def __init__(self, pattern, loose=False):
        self.pattern = pattern
        self.loose = loose
        if loose:
            self.partial = self.partial_loose
        ranges = list(map(self._parse_range, self.pattern.split('||')))
        self.ranges = self._sort_ranges(ranges)

    def _parse_range(self, group):
        group = self._expand_hyphen_ranges(group.strip() or '*')
        group = self._expand_advanced_operators(group)
        return self._create_comparators(group)

    def _parse_partial_version(self, version):
        # NB: allows partial versions, drops pre_release and build parts
        blank = {'*', 'x', 'X'}
        split_version = version
        if self.loose and split_version.startswith('v'):
            split_version = split_version[1:]
        split_version = split_version.split('.', 2)
        if len(split_version) == 3:
            split_version[2] = re.sub(r'[+-].*$', '', split_version[2])
            if self.loose:
                split_version[2] = re.sub(r'^(\d+).*$', '\\1', split_version[2])

        def parse(item):
            part, name = item
            if part in blank:
                return None
            return parse_int(name, part, loose=self.loose)

        split_version = map(parse, zip(split_version, ('major', 'minor', 'patch')))
        split_version = list(itertools.islice(itertools.chain(split_version, itertools.repeat(None)), 3))
        incomplete = None
        for i in range(3):
            if split_version[i] is not None:
                continue
            incomplete = i
            if any(subsequent is not None for subsequent in split_version[i + 1:]):
                raise ValueError('Partial version %s is invalid' % version)
            break
        if incomplete is None:
            split_version_zeroed = split_version
        else:
            split_version_zeroed = split_version[:incomplete] + [0] * (3 - incomplete)
        return split_version_zeroed, incomplete

    def _expand_hyphen_ranges(self, group):
        def convert_limit(match, end):
            version = match.group(end)
            zeroed, incomplete = self._parse_partial_version(version)
            if incomplete == 0:
                if end == 'lower':
                    version = '0.0.0'
                else:
                    version = '*.*.*'
            elif incomplete is not None:
                if end == 'higher':
                    zeroed[incomplete - 1] += 1
                version = '.'.join(map(str, zeroed))
            if end == 'lower':
                comparator = '>='
            elif incomplete is None:
                comparator = '<='
            else:
                comparator = '<'
            return comparator, version

        def hyphen_range(match):
            lower_comparator, lower = convert_limit(match, 'lower')
            higher_comparator, higher = convert_limit(match, 'higher')
            if higher == '*.*.*':
                return '%s%s' % (lower_comparator, lower)
            return '%s%s %s%s' % (lower_comparator, lower, higher_comparator, higher)

        return re.sub(
            r'(?P<lower>%s)\s+-\s+(?P<higher>%s)' % (self.partial, self.partial),
            hyphen_range,
            group
        )

    def _expand_advanced_operators(self, group):
        def advanced_operator(match):
            operator = match.group('operator')
            version = match.group('version')
            version_max, incomplete = self._parse_partial_version(version)
            version_min = version if incomplete is None else '.'.join(map(str, version_max))

            if operator.startswith('~'):
                if incomplete in (0, 1):
                    version_max[0] += 1
                    version_max[1] = 0
                else:
                    version_max[1] += 1
                version_max[2] = 0
                return '>=%s <%s' % (version_min, '.'.join(map(str, version_max)))

            if operator == '^':
                if incomplete == 0:
                    # presumably ^* matches anything
                    return '>=0.0.0'
                elif version_max[0] != 0 or incomplete == 1:
                    version_max[0] += 1
                    version_max[1] = 0
                    version_max[2] = 0
                elif version_max[0] == 0 and (version_max[1] != 0 or incomplete == 2):
                    version_max[1] += 1
                    version_max[2] = 0
                else:
                    version_max[2] += 1
                return '>=%s <%s' % (version_min, '.'.join(map(str, version_max)))

            raise ValueError('Unknown operator %s' % operator)

        return re.sub(
            r'(?P<operator>~>?|\^)\s*(?P<version>%s)' % self.partial,
            advanced_operator,
            group
        )

    def _create_comparators(self, group):
        group = re.sub(r'(<|>|<=|>=|=)\s+', r'\1', group)
        comparators = []
        for comparator in group.split():
            if comparator.startswith('>='):
                self._create_comparator(comparators, '__ge__', comparator[2:])
            elif comparator.startswith('>'):
                self._create_comparator(comparators, '__gt__', comparator[1:])
            elif comparator.startswith('<='):
                self._create_comparator(comparators, '__le__', comparator[2:])
            elif comparator.startswith('<'):
                self._create_comparator(comparators, '__lt__', comparator[1:])
            elif comparator.startswith('='):
                self._create_comparator(comparators, '__eq__', comparator[1:])
            else:
                self._create_comparator(comparators, '__eq__', comparator)
        comparators = self._sort_comparators(comparators)

        def comparator(version):
            if version.pre_release:
                version = version.without_build
                return any(
                    getattr(version, operator)(limit.without_build)
                    for operator, limit in comparators
                    if operator in {'__eq__', '__le__', '__ge__'} and limit.pre_release
                )
            return all(
                getattr(version, operator)(limit)
                for operator, limit in comparators
            )

        operators = {
            '__eq__': '',
            '__ge__': '>=',
            '__gt__': '>',
            '__lt__': '<',
            '__le__': '<=',
        }
        comparator.desc = ' '.join('%s%s' % (operators[operator], limit) for operator, limit in comparators)
        return comparator

    def _create_comparator(self, comparators, operator, limit):
        try:
            pre_release = Version(limit, loose=self.loose).pre_release
        except ValueError:
            pre_release = ''
        limit, incomplete = self._parse_partial_version(limit)
        if incomplete is not None:
            pre_release = ''
            operator, limit = self._adjust_comparator(comparators, operator, limit, incomplete)
        limit = '.'.join(map(str, limit))
        if pre_release:
            limit = '%s-%s' % (limit, pre_release)
        limit = Version(limit, loose=self.loose)
        comparators.append((operator, limit))

    def _adjust_comparator(self, comparators, operator, limit, incomplete):
        if incomplete == 0:
            # TODO: fix * handling so that comparator simplification can take it into account
            return '__lt__' if operator in ('__lt__', '__gt__') else '__ge__', [0, 0, 0]
        if operator in ('__lt__', '__le__'):
            if operator == '__le__':
                limit = self._increment_limit(limit, incomplete)
            operator = '__lt__'
        elif operator in ('__gt__', '__ge__'):
            if operator == '__gt__':
                limit = self._increment_limit(limit, incomplete)
            operator = '__ge__'
        elif operator == '__eq__':
            if incomplete in (1, 2):
                upper = self._increment_limit(limit, incomplete)
                comparators.append(('__lt__', Version('.'.join(map(str, upper)), loose=self.loose)))
            operator = '__ge__'
        return operator, limit

    def _increment_limit(self, limit, incomplete):
        limit = limit.copy()
        limit[incomplete - 1] += 1
        for i in range(incomplete, 3):
            limit[i] = 0
        return limit

    def _sort_comparators(self, comparators):
        # TODO: simplify overlapping comparators
        precedence = {
            '__eq__': 0,
            '__ge__': 1,
            '__gt__': 2,
            '__lt__': 3,
            '__le__': 4,
        }
        comparators = sorted(comparators, key=lambda comparator: (comparator[1], precedence[comparator[0]]))
        return comparators

    def _sort_ranges(self, ranges):
        # TODO: improve de-duplication? e.g. when one range entirely covers another range's comparators
        used_patterns = set()
        new_ranges = []
        for comparator in ranges:
            if comparator.desc in used_patterns:
                continue
            new_ranges.append(comparator)
            used_patterns.add(comparator.desc)
        return new_ranges

    def __str__(self):
        # TODO: improve normalisation?
        pattern = self.pattern.strip()
        pattern = pattern.replace('||', ' || ')
        pattern = pattern.replace('~>', '~')
        pattern = re.sub(r'(<|>|<=|>=|=|\^|~)\s+', r'\1', pattern)
        pattern = re.sub(r'\s+', ' ', pattern)
        return pattern

    def __repr__(self):
        return '<Range "%s">' % self

    def __hash__(self):
        return hash(str(self))

    def __copy__(self):
        raise self.__class__(str(self), loose=self.loose)

    def __contains__(self, version):
        if not isinstance(version, Version):
            version = Version(version, loose=self.loose)
        return any(group(version) for group in self.ranges)

    def __or__(self, other):
        cls = type(self)
        if isinstance(other, str):
            other = cls(other)
        elif not isinstance(other, cls):
            raise TypeError('%r is not a range' % other)
        return cls('%s||%s' % (self, other), loose=self.loose or other.loose)

    def lowest_version(self, versions):
        versions = map(
            lambda version: version if isinstance(version, Version) else Version(version, loose=self.loose),
            versions
        )
        versions = sorted(filter(lambda version: version in self, versions))
        if versions:
            return versions[0]

    def highest_version(self, versions):
        versions = map(
            lambda version: version if isinstance(version, Version) else Version(version, loose=self.loose),
            versions
        )
        versions = sorted(filter(lambda version: version in self, versions))
        if versions:
            return versions[-1]
