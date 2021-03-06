import subprocess
import unittest


from semver_range import Version, Range


class VersionTestCase(unittest.TestCase):
    # largely taken from https://github.com/npm/node-semver/blob/master/test/index.js

    def test_invalid(self):
        data = [
            '1.2.3.4',
            'NOT VALID',
            1.2,
            None,
            '',
        ]
        for version in data:
            with self.assertRaises(ValueError, msg='Version should be invalid %s' % version):
                Version(version)

    def test_loose(self):
        data = [
            ['=1.2.3', '1.2.3'],
            ['01.02.03', '1.2.3'],
            ['1.2.3-beta.01', '1.2.3-beta.1'],
            ['   =1.2.3', '1.2.3'],
            ['1.2.3foo', '1.2.3-foo'],
        ]
        for loose, strict in data:
            with self.assertRaises(ValueError, msg='Version should be strictly invalid %s' % loose):
                Version(loose)
            loose = Version(loose, loose=True)
            self.assertEqual(loose, strict)
            self.assertTrue(loose.has_same_precedence(strict))

    def test_versions(self):
        data = [
            ['0.0.0', '0.0.0-foo'],
            ['0.0.1', '0.0.0'],
            ['1.0.0', '0.9.9'],
            ['0.10.0', '0.9.0'],
            ['0.99.0', '0.10.0'],
            ['2.0.0', '1.2.3'],
            ['1.2.3', '1.2.3-asdf'],
            ['1.2.3', '1.2.3-4'],
            ['1.2.3', '1.2.3-4-foo'],
            ['1.2.3-5-foo', '1.2.3-5'],
            ['1.2.3-5', '1.2.3-4'],
            ['1.2.3-5-foo', '1.2.3-5-Foo'],
            ['3.0.0', '2.7.2+asdf'],
            ['1.2.3-a.10', '1.2.3-a.5'],
            ['1.2.3-a.b', '1.2.3-a.5'],
            ['1.2.3-a.b', '1.2.3-a'],
            ['1.2.3-a.b.c.10.d.5', '1.2.3-a.b.c.5.d.100'],
            ['1.2.3-r2', '1.2.3-r100'],
            ['1.2.3-r100', '1.2.3-R2'],
        ]
        for v1, v2 in data:
            v1 = Version(v1)
            v2 = Version(v2)
            self.assertGreater(v1, v2)
            self.assertGreaterEqual(v1, v2)
            self.assertLess(v2, v1)
            self.assertLessEqual(v2, v1)
            self.assertNotEqual(v1, v2)
            # self.assertTrue(v2.precedes(v1), msg='%s should precede %s' % (v2, v1))

    def test_loose_comparison(self):
        data = [
            ['v0.0.0', '0.0.0-foo'],
            ['v0.0.1', '0.0.0'],
            ['v1.0.0', '0.9.9'],
            ['v0.10.0', '0.9.0'],
            ['v0.99.0', '0.10.0'],
            ['v2.0.0', '1.2.3'],
            ['0.0.0', 'v0.0.0-foo'],
            ['0.0.1', 'v0.0.0'],
            ['1.0.0', 'v0.9.9'],
            ['0.10.0', 'v0.9.0'],
            ['0.99.0', 'v0.10.0'],
            ['2.0.0', 'v1.2.3'],
        ]
        for v1, v2 in data:
            v1 = Version(v1, loose=True)
            v2 = Version(v2, loose=True)
            self.assertGreater(v1, v2)
            self.assertGreaterEqual(v1, v2)
            self.assertLess(v2, v1)
            self.assertLessEqual(v2, v1)
            self.assertNotEqual(v1, v2)
            self.assertTrue(v2.precedes(v1))

    def test_loosely_matching_precedence(self):
        data = [
            ['1.2.3', 'v1.2.3'],
            ['1.2.3', '=1.2.3'],
            ['1.2.3', 'v 1.2.3'],
            ['1.2.3', '= 1.2.3'],
            ['1.2.3', ' v1.2.3'],
            ['1.2.3', ' =1.2.3'],
            ['1.2.3', ' v 1.2.3'],
            ['1.2.3', ' = 1.2.3'],
            ['1.2.3-0', 'v1.2.3-0'],
            ['1.2.3-0', '=1.2.3-0'],
            ['1.2.3-0', 'v 1.2.3-0'],
            ['1.2.3-0', '= 1.2.3-0'],
            ['1.2.3-0', ' v1.2.3-0'],
            ['1.2.3-0', ' =1.2.3-0'],
            ['1.2.3-0', ' v 1.2.3-0'],
            ['1.2.3-0', ' = 1.2.3-0'],
            ['1.2.3-1', 'v1.2.3-1'],
            ['1.2.3-1', '=1.2.3-1'],
            ['1.2.3-1', 'v 1.2.3-1'],
            ['1.2.3-1', '= 1.2.3-1'],
            ['1.2.3-1', ' v1.2.3-1'],
            ['1.2.3-1', ' =1.2.3-1'],
            ['1.2.3-1', ' v 1.2.3-1'],
            ['1.2.3-1', ' = 1.2.3-1'],
            ['1.2.3-beta', 'v1.2.3-beta'],
            ['1.2.3-beta', '=1.2.3-beta'],
            ['1.2.3-beta', 'v 1.2.3-beta'],
            ['1.2.3-beta', '= 1.2.3-beta'],
            ['1.2.3-beta', ' v1.2.3-beta'],
            ['1.2.3-beta', ' =1.2.3-beta'],
            ['1.2.3-beta', ' v 1.2.3-beta'],
            ['1.2.3-beta', ' = 1.2.3-beta'],
        ]
        for v1, v2 in data:
            v1 = Version(v1, loose=True)
            v2 = Version(v2, loose=True)
            self.assertEqual(v1, v2)
            self.assertTrue(v1.has_same_precedence(v2))

        data += [
            ['1.2.3-beta+build', ' = 1.2.3-beta+otherbuild'],
            ['1.2.3+build', ' = 1.2.3+otherbuild'],
            ['1.2.3-beta+build', '1.2.3-beta+otherbuild'],
            ['1.2.3+build', '1.2.3+otherbuild'],
            ['  v1.2.3+build', '1.2.3+otherbuild'],
        ]
        for v1, v2 in data:
            v1 = Version(v1, loose=True)
            v2 = Version(v2, loose=True)
            self.assertTrue(v1.has_same_precedence(v2))

    def test_incrementing(self):
        data = [
            ['1.2.3', 'major', '2.0.0'],
            ['1.2.3', 'minor', '1.3.0'],
            ['1.2.3', 'patch', '1.2.4'],
            ['1.2.3tag', 'major', '2.0.0', True],
            ['1.2.3-tag', 'major', '2.0.0'],
            ['1.2.3', 'fake', None],
            ['1.2.0-0', 'patch', '1.2.0'],
            ['fake', 'major', None],
            ['1.2.3-4', 'major', '2.0.0'],
            ['1.2.3-4', 'minor', '1.3.0'],
            ['1.2.3-4', 'patch', '1.2.3'],
            ['1.2.3-alpha.0.beta', 'major', '2.0.0'],
            ['1.2.3-alpha.0.beta', 'minor', '1.3.0'],
            ['1.2.3-alpha.0.beta', 'patch', '1.2.3'],
            ['1.2.4', 'prerelease', '1.2.5-0'],
            ['1.2.3-0', 'prerelease', '1.2.3-1'],
            ['1.2.3-alpha.0', 'prerelease', '1.2.3-alpha.1'],
            ['1.2.3-alpha.1', 'prerelease', '1.2.3-alpha.2'],
            ['1.2.3-alpha.2', 'prerelease', '1.2.3-alpha.3'],
            ['1.2.3-alpha.0.beta', 'prerelease', '1.2.3-alpha.1.beta'],
            ['1.2.3-alpha.1.beta', 'prerelease', '1.2.3-alpha.2.beta'],
            ['1.2.3-alpha.2.beta', 'prerelease', '1.2.3-alpha.3.beta'],
            ['1.2.3-alpha.10.0.beta', 'prerelease', '1.2.3-alpha.10.1.beta'],
            ['1.2.3-alpha.10.1.beta', 'prerelease', '1.2.3-alpha.10.2.beta'],
            ['1.2.3-alpha.10.2.beta', 'prerelease', '1.2.3-alpha.10.3.beta'],
            ['1.2.3-alpha.10.beta.0', 'prerelease', '1.2.3-alpha.10.beta.1'],
            ['1.2.3-alpha.10.beta.1', 'prerelease', '1.2.3-alpha.10.beta.2'],
            ['1.2.3-alpha.10.beta.2', 'prerelease', '1.2.3-alpha.10.beta.3'],
            ['1.2.3-alpha.9.beta', 'prerelease', '1.2.3-alpha.10.beta'],
            ['1.2.3-alpha.10.beta', 'prerelease', '1.2.3-alpha.11.beta'],
            ['1.2.3-alpha.11.beta', 'prerelease', '1.2.3-alpha.12.beta'],
            ['1.2.0', 'prepatch', '1.2.1-0'],
            ['1.2.0-1', 'prepatch', '1.2.1-0'],
            ['1.2.0', 'preminor', '1.3.0-0'],
            ['1.2.3-1', 'preminor', '1.3.0-0'],
            ['1.2.0', 'premajor', '2.0.0-0'],
            ['1.2.3-1', 'premajor', '2.0.0-0'],
            ['1.2.0-1', 'minor', '1.2.0'],
            ['1.0.0-1', 'major', '1.0.0'],
        ]
        for row in data:
            if len(row) == 4:
                version, level, expected, loose = row
            else:
                version, level, expected = row
                loose = False
            msg = 'Incrementing %s by %s' % (version, level)
            if expected is None:
                with self.assertRaises(ValueError):
                    version = Version(version, loose=loose)
                    self.assertEqual(version.increment(level), expected, msg=msg)
                continue
            version = Version(version, loose=loose)
            self.assertEqual(version.increment(level), expected, msg=msg)

    @unittest.skip('Not implemented')
    def test_incrementing_with_pre_release(self):
        data = [
            ['1.2.3', 'major', '2.0.0', False, 'dev'],
            ['1.2.3', 'minor', '1.3.0', False, 'dev'],
            ['1.2.3', 'patch', '1.2.4', False, 'dev'],
            ['1.2.3tag', 'major', '2.0.0', True, 'dev'],
            ['1.2.3-tag', 'major', '2.0.0', False, 'dev'],
            ['1.2.3', 'fake', None, False, 'dev'],
            ['1.2.0-0', 'patch', '1.2.0', False, 'dev'],
            ['fake', 'major',  None, False, 'dev'],
            ['1.2.3-4', 'major', '2.0.0', False, 'dev'],
            ['1.2.3-4', 'minor', '1.3.0', False, 'dev'],
            ['1.2.3-4', 'patch', '1.2.3', False, 'dev'],
            ['1.2.3-alpha.0.beta', 'major', '2.0.0', False, 'dev'],
            ['1.2.3-alpha.0.beta', 'minor', '1.3.0', False, 'dev'],
            ['1.2.3-alpha.0.beta', 'patch', '1.2.3', False, 'dev'],
            ['1.2.4', 'prerelease', '1.2.5-dev.0', False, 'dev'],
            ['1.2.3-0', 'prerelease', '1.2.3-dev.0', False, 'dev'],
            ['1.2.3-alpha.0', 'prerelease', '1.2.3-dev.0', False, 'dev'],
            ['1.2.3-alpha.0', 'prerelease', '1.2.3-alpha.1', False, 'alpha'],
            ['1.2.3-alpha.0.beta', 'prerelease', '1.2.3-dev.0', False, 'dev'],
            ['1.2.3-alpha.0.beta', 'prerelease', '1.2.3-alpha.1.beta', False, 'alpha'],
            ['1.2.3-alpha.10.0.beta', 'prerelease', '1.2.3-dev.0', False, 'dev'],
            ['1.2.3-alpha.10.0.beta', 'prerelease', '1.2.3-alpha.10.1.beta', False, 'alpha'],
            ['1.2.3-alpha.10.1.beta', 'prerelease', '1.2.3-alpha.10.2.beta', False, 'alpha'],
            ['1.2.3-alpha.10.2.beta', 'prerelease', '1.2.3-alpha.10.3.beta', False, 'alpha'],
            ['1.2.3-alpha.10.beta.0', 'prerelease', '1.2.3-dev.0', False, 'dev'],
            ['1.2.3-alpha.10.beta.0', 'prerelease', '1.2.3-alpha.10.beta.1', False, 'alpha'],
            ['1.2.3-alpha.10.beta.1', 'prerelease', '1.2.3-alpha.10.beta.2', False, 'alpha'],
            ['1.2.3-alpha.10.beta.2', 'prerelease', '1.2.3-alpha.10.beta.3', False, 'alpha'],
            ['1.2.3-alpha.9.beta', 'prerelease', '1.2.3-dev.0', False, 'dev'],
            ['1.2.3-alpha.9.beta', 'prerelease', '1.2.3-alpha.10.beta', False, 'alpha'],
            ['1.2.3-alpha.10.beta', 'prerelease', '1.2.3-alpha.11.beta', False, 'alpha'],
            ['1.2.3-alpha.11.beta', 'prerelease', '1.2.3-alpha.12.beta', False, 'alpha'],
            ['1.2.0', 'prepatch', '1.2.1-dev.0', False, 'dev'],
            ['1.2.0-1', 'prepatch', '1.2.1-dev.0', False, 'dev'],
            ['1.2.0', 'preminor', '1.3.0-dev.0', False, 'dev'],
            ['1.2.3-1', 'preminor', '1.3.0-dev.0', False, 'dev'],
            ['1.2.0', 'premajor', '2.0.0-dev.0', False, 'dev'],
            ['1.2.3-1', 'premajor', '2.0.0-dev.0', False, 'dev'],
            ['1.2.0-1', 'minor', '1.2.0', False, 'dev'],
            ['1.0.0-1', 'major', '1.0.0', False, 'dev'],
            ['1.2.3-dev.bar', 'prerelease', '1.2.3-dev.0', False, 'dev'],
        ]
        for version, level, expected, loose, identifier in data:
            msg = 'Incrementing %s by %s with identifier %s' % (version, level, identifier)
            version = Version(version, loose=loose)
            self.assertEqual(version.increment(level, identifier=identifier), expected, msg=msg)


class RangeTestCase(unittest.TestCase):
    # largely taken from https://github.com/npm/node-semver/blob/master/test/index.js

    def test_ranges(self):
        data = [
            ['1.2.3 - 2.3.4', '>=1.2.3 <=2.3.4'],
            ['1.2 - 2.3.4', '>=1.2.0 <=2.3.4'],
            ['1.2.3 - 2.3', '>=1.2.3 <2.4.0'],
            ['1.2.3 - 2', '>=1.2.3 <3.0.0'],

            ['~1.2.3', '>=1.2.3 <1.3.0'],
            ['~1.2', '>=1.2.0 <1.3.0'],
            ['~1', '>=1.0.0 <2.0.0'],
            ['~0.2.3', '>=0.2.3 <0.3.0'],
            ['~0.2', '>=0.2.0 <0.3.0'],
            ['~0', '>=0.0.0 <1.0.0'],
            ['~1.2.3-beta.2', '>=1.2.3-beta.2 <1.3.0'],

            ['^1.2.3', '>=1.2.3 <2.0.0'],
            ['^0.2.3', '>=0.2.3 <0.3.0'],
            ['^0.0.3', '>=0.0.3 <0.0.4'],
            ['^1.2.3-beta.2', '>=1.2.3-beta.2 <2.0.0'],
            ['^0.0.3-beta', '>=0.0.3-beta <0.0.4'],
            ['^1.2.x', '>=1.2.0 <2.0.0'],
            ['^0.0.x', '>=0.0.0 <0.1.0'],
            ['^0.0', '>=0.0.0 <0.1.0'],
            ['^1.x', '>=1.0.0 <2.0.0'],
            ['^0.x', '>=0.0.0 <1.0.0'],

            ['1.2.3 - *', '>=1.2.3'],
            ['* - 2', '>=0.0.0 <3.0.0'],
            ['^*', '>=0.0.0'],  # is this right?
            ['', '>=0.0.0'],

            ['1.0.0 - 2.0.0', '>=1.0.0 <=2.0.0'],
            ['1.0.0', '1.0.0'],
            ['>=*', '>=0.0.0'],  # node's semver uses *
            ['', '>=0.0.0'],  # node's semver uses *
            ['*', '>=0.0.0'],  # node's semver uses *
            ['*', '>=0.0.0'],  # node's semver uses *
            ['>=1.0.0', '>=1.0.0'],
            ['>1.0.0', '>1.0.0'],
            ['<=2.0.0', '<=2.0.0'],
            ['1', '>=1.0.0 <2.0.0'],
            ['<=2.0.0', '<=2.0.0'],
            ['<=2.0.0', '<=2.0.0'],
            ['<2.0.0', '<2.0.0'],
            ['<2.0.0', '<2.0.0'],
            ['>= 1.0.0', '>=1.0.0'],
            ['>=  1.0.0', '>=1.0.0'],
            ['>=   1.0.0', '>=1.0.0'],
            ['> 1.0.0', '>1.0.0'],
            ['>  1.0.0', '>1.0.0'],
            ['<=   2.0.0', '<=2.0.0'],
            ['<= 2.0.0', '<=2.0.0'],
            ['<=  2.0.0', '<=2.0.0'],
            ['<    2.0.0', '<2.0.0'],
            ['<	2.0.0', '<2.0.0'],
            ['>=0.1.97', '>=0.1.97'],
            ['>=0.1.97', '>=0.1.97'],
            ['0.1.20 || 1.2.4', '0.1.20||1.2.4'],
            ['>=0.2.3 || <0.0.1', '>=0.2.3||<0.0.1'],
            ['>=0.2.3 || <0.0.1', '>=0.2.3||<0.0.1'],
            ['>=0.2.3 || <0.0.1', '>=0.2.3||<0.0.1'],
            ['||', '>=0.0.0'],  # node's semver uses ||
            ['2.x.x', '>=2.0.0 <3.0.0'],
            ['1.2.x', '>=1.2.0 <1.3.0'],
            ['1.2.x || 2.x', '>=1.2.0 <1.3.0||>=2.0.0 <3.0.0'],
            ['1.2.x || 2.x', '>=1.2.0 <1.3.0||>=2.0.0 <3.0.0'],
            ['x', '>=0.0.0'],  # node's semver uses *
            ['2.*.*', '>=2.0.0 <3.0.0'],
            ['1.2.*', '>=1.2.0 <1.3.0'],
            ['1.2.* || 2.*', '>=1.2.0 <1.3.0||>=2.0.0 <3.0.0'],
            ['*', '>=0.0.0'],  # node's semver uses *
            ['2', '>=2.0.0 <3.0.0'],
            ['2.3', '>=2.3.0 <2.4.0'],
            ['~2.4', '>=2.4.0 <2.5.0'],
            ['~2.4', '>=2.4.0 <2.5.0'],
            ['~>3.2.1', '>=3.2.1 <3.3.0'],
            ['~1', '>=1.0.0 <2.0.0'],
            ['~>1', '>=1.0.0 <2.0.0'],
            ['~> 1', '>=1.0.0 <2.0.0'],
            ['~1.0', '>=1.0.0 <1.1.0'],
            ['~ 1.0', '>=1.0.0 <1.1.0'],
            ['^0', '>=0.0.0 <1.0.0'],
            ['^ 1', '>=1.0.0 <2.0.0'],
            ['^0.1', '>=0.1.0 <0.2.0'],
            ['^1.0', '>=1.0.0 <2.0.0'],
            ['^1.2', '>=1.2.0 <2.0.0'],
            ['^0.0.1', '>=0.0.1 <0.0.2'],
            ['^0.0.1-beta', '>=0.0.1-beta <0.0.2'],
            ['^0.1.2', '>=0.1.2 <0.2.0'],
            ['^1.2.3', '>=1.2.3 <2.0.0'],
            ['^1.2.3-beta.4', '>=1.2.3-beta.4 <2.0.0'],
            ['<1', '<1.0.0'],
            ['< 1', '<1.0.0'],
            ['>=1', '>=1.0.0'],
            ['>= 1', '>=1.0.0'],
            ['<1.2', '<1.2.0'],
            ['< 1.2', '<1.2.0'],
            ['1', '>=1.0.0 <2.0.0'],
            ['^ 1.2 ^ 1', '>=1.0.0 >=1.2.0 <2.0.0 <2.0.0'],  # node's semver doesn't sort: >=1.2.0 <2.0.0 >=1.0.0 <2.0.0
        ]
        for pattern, expanded in data:
            pattern = Range(pattern)
            result = '||'.join(comparator.desc for comparator in pattern.ranges)
            self.assertEqual(result, expanded, msg='%s should expand to %s' % (pattern, expanded))

    def test_loose_ranges(self):
        data = [
            ['>01.02.03', '>1.2.3'],
            ['~1.2.3beta', '>=1.2.3-beta <1.3.0'],
        ]
        for pattern, expanded in data:
            pattern = Range(pattern, loose=True)
            result = '||'.join(comparator.desc for comparator in pattern.ranges)
            self.assertEqual(result, expanded, msg='%s should expand to %s' % (pattern, expanded))

    def test_comparators(self):
        data = [
            ['1.0.0 - 2.0.0', [['>=1.0.0', '<=2.0.0']]],
            ['1.0.0', [['1.0.0']]],
            ['>=*', [['>=0.0.0']]],  # node's semver uses ''
            ['', [['>=0.0.0']]],  # node's semver uses ''
            ['*', [['>=0.0.0']]],  # node's semver uses ''
            ['*', [['>=0.0.0']]],  # node's semver uses ''
            ['>=1.0.0', [['>=1.0.0']]],
            ['>=1.0.0', [['>=1.0.0']]],
            ['>=1.0.0', [['>=1.0.0']]],
            ['>1.0.0', [['>1.0.0']]],
            ['>1.0.0', [['>1.0.0']]],
            ['<=2.0.0', [['<=2.0.0']]],
            ['1', [['>=1.0.0', '<2.0.0']]],
            ['<=2.0.0', [['<=2.0.0']]],
            ['<=2.0.0', [['<=2.0.0']]],
            ['<2.0.0', [['<2.0.0']]],
            ['<2.0.0', [['<2.0.0']]],
            ['>= 1.0.0', [['>=1.0.0']]],
            ['>=  1.0.0', [['>=1.0.0']]],
            ['>=   1.0.0', [['>=1.0.0']]],
            ['> 1.0.0', [['>1.0.0']]],
            ['>  1.0.0', [['>1.0.0']]],
            ['<=   2.0.0', [['<=2.0.0']]],
            ['<= 2.0.0', [['<=2.0.0']]],
            ['<=  2.0.0', [['<=2.0.0']]],
            ['<    2.0.0', [['<2.0.0']]],
            ['<\t2.0.0', [['<2.0.0']]],
            ['>=0.1.97', [['>=0.1.97']]],
            ['>=0.1.97', [['>=0.1.97']]],
            ['0.1.20 || 1.2.4', [['0.1.20'], ['1.2.4']]],
            ['>=0.2.3 || <0.0.1', [['>=0.2.3'], ['<0.0.1']]],
            ['>=0.2.3 || <0.0.1', [['>=0.2.3'], ['<0.0.1']]],
            ['>=0.2.3 || <0.0.1', [['>=0.2.3'], ['<0.0.1']]],
            ['||', [['>=0.0.0']]],  # node's semver uses '||'
            ['2.x.x', [['>=2.0.0', '<3.0.0']]],
            ['1.2.x', [['>=1.2.0', '<1.3.0']]],
            ['1.2.x || 2.x', [['>=1.2.0', '<1.3.0'], ['>=2.0.0', '<3.0.0']]],
            ['1.2.x || 2.x', [['>=1.2.0', '<1.3.0'], ['>=2.0.0', '<3.0.0']]],
            ['x', [['>=0.0.0']]],  # node's semver uses ''
            ['2.*.*', [['>=2.0.0', '<3.0.0']]],
            ['1.2.*', [['>=1.2.0', '<1.3.0']]],
            ['1.2.* || 2.*', [['>=1.2.0', '<1.3.0'], ['>=2.0.0', '<3.0.0']]],
            ['1.2.* || 2.*', [['>=1.2.0', '<1.3.0'], ['>=2.0.0', '<3.0.0']]],
            ['*', [['>=0.0.0']]],  # node's semver uses ''
            ['2', [['>=2.0.0', '<3.0.0']]],
            ['2.3', [['>=2.3.0', '<2.4.0']]],
            ['~2.4', [['>=2.4.0', '<2.5.0']]],
            ['~2.4', [['>=2.4.0', '<2.5.0']]],
            ['~>3.2.1', [['>=3.2.1', '<3.3.0']]],
            ['~1', [['>=1.0.0', '<2.0.0']]],
            ['~>1', [['>=1.0.0', '<2.0.0']]],
            ['~> 1', [['>=1.0.0', '<2.0.0']]],
            ['~1.0', [['>=1.0.0', '<1.1.0']]],
            ['~ 1.0', [['>=1.0.0', '<1.1.0']]],
            ['~ 1.0.3', [['>=1.0.3', '<1.1.0']]],
            ['~> 1.0.3', [['>=1.0.3', '<1.1.0']]],
            ['<1', [['<1.0.0']]],
            ['< 1', [['<1.0.0']]],
            ['>=1', [['>=1.0.0']]],
            ['>= 1', [['>=1.0.0']]],
            ['<1.2', [['<1.2.0']]],
            ['< 1.2', [['<1.2.0']]],
            ['1', [['>=1.0.0', '<2.0.0']]],
            # node's semver uses '>=1.0.0', '<2.0.0', '>=2.0.0', '<3.0.0':
            ['1 2', [['>=1.0.0', '>=2.0.0', '<2.0.0', '<3.0.0']]],
            ['1.2 - 3.4.5', [['>=1.2.0', '<=3.4.5']]],
            ['1.2.3 - 3.4', [['>=1.2.3', '<3.5.0']]],
            ['1.2.3 - 3', [['>=1.2.3', '<4.0.0']]],

            # match-nothing ranges
            ['>*', [['<0.0.0']]],
            ['<*', [['<0.0.0']]],
        ]
        for pattern, expected_ranges in data:
            pattern = Range(pattern)
            for expected_range, comparator in zip(expected_ranges, pattern.ranges):
                expected_range = ' '.join(expected_range)
                self.assertEqual(expected_range, comparator.desc,
                                 msg='%s should expand to %s' % (pattern, expected_range))

    def test_range_matches(self):
        data = [
            ['1.0.0 - 2.0.0', '1.2.3'],
            ['^1.2.3+build', '1.2.3'],
            ['^1.2.3+build', '1.3.0'],
            ['1.2.3-pre+asdf - 2.4.3-pre+asdf', '1.2.3'],
            ['1.2.3-pre+asdf - 2.4.3-pre+asdf', '1.2.3-pre.2'],
            ['1.2.3-pre+asdf - 2.4.3-pre+asdf', '2.4.3-alpha'],
            ['1.2.3+asdf - 2.4.3+asdf', '1.2.3'],
            ['1.0.0', '1.0.0'],
            ['>=*', '0.2.4'],
            ['', '1.0.0'],
            ['*', '1.2.3'],
            ['>=1.0.0', '1.0.0'],
            ['>=1.0.0', '1.0.1'],
            ['>=1.0.0', '1.1.0'],
            ['>1.0.0', '1.0.1'],
            ['>1.0.0', '1.1.0'],
            ['<=2.0.0', '2.0.0'],
            ['<=2.0.0', '1.9999.9999'],
            ['<=2.0.0', '0.2.9'],
            ['<2.0.0', '1.9999.9999'],
            ['<2.0.0', '0.2.9'],
            ['>= 1.0.0', '1.0.0'],
            ['>=  1.0.0', '1.0.1'],
            ['>=   1.0.0', '1.1.0'],
            ['> 1.0.0', '1.0.1'],
            ['>  1.0.0', '1.1.0'],
            ['<=   2.0.0', '2.0.0'],
            ['<= 2.0.0', '1.9999.9999'],
            ['<=  2.0.0', '0.2.9'],
            ['<    2.0.0', '1.9999.9999'],
            ['<\t2.0.0', '0.2.9'],
            ['>=0.1.97', '0.1.97'],
            ['0.1.20 || 1.2.4', '1.2.4'],
            ['>=0.2.3 || <0.0.1', '0.0.0'],
            ['>=0.2.3 || <0.0.1', '0.2.3'],
            ['>=0.2.3 || <0.0.1', '0.2.4'],
            ['||', '1.3.4'],
            ['2.x.x', '2.1.3'],
            ['1.2.x', '1.2.3'],
            ['1.2.x || 2.x', '2.1.3'],
            ['1.2.x || 2.x', '1.2.3'],
            ['x', '1.2.3'],
            ['2.*.*', '2.1.3'],
            ['1.2.*', '1.2.3'],
            ['1.2.* || 2.*', '2.1.3'],
            ['1.2.* || 2.*', '1.2.3'],
            ['*', '1.2.3'],
            ['2', '2.1.2'],
            ['2.3', '2.3.1'],
            ['~2.4', '2.4.0'],  # >=2.4.0 <2.5.0
            ['~2.4', '2.4.5'],
            ['~>3.2.1', '3.2.2'],  # >=3.2.1 <3.3.0,
            ['~1', '1.2.3'],  # >=1.0.0 <2.0.0
            ['~>1', '1.2.3'],
            ['~> 1', '1.2.3'],
            ['~1.0', '1.0.2'],  # >=1.0.0 <1.1.0,
            ['~ 1.0', '1.0.2'],
            ['~ 1.0.3', '1.0.12'],
            ['>=1', '1.0.0'],
            ['>= 1', '1.0.0'],
            ['<1.2', '1.1.1'],
            ['< 1.2', '1.1.1'],
            ['=0.7.x', '0.7.2'],
            ['<=0.7.x', '0.7.2'],
            ['>=0.7.x', '0.7.2'],
            ['<=0.7.x', '0.6.2'],
            ['~1.2.1 >=1.2.3', '1.2.3'],
            ['~1.2.1 =1.2.3', '1.2.3'],
            ['~1.2.1 1.2.3', '1.2.3'],
            ['~1.2.1 >=1.2.3 1.2.3', '1.2.3'],
            ['~1.2.1 1.2.3 >=1.2.3', '1.2.3'],
            ['~1.2.1 1.2.3', '1.2.3'],
            ['>=1.2.1 1.2.3', '1.2.3'],
            ['1.2.3 >=1.2.1', '1.2.3'],
            ['>=1.2.3 >=1.2.1', '1.2.3'],
            ['>=1.2.1 >=1.2.3', '1.2.3'],
            ['>=1.2', '1.2.8'],
            ['^1.2.3', '1.8.1'],
            ['^0.1.2', '0.1.2'],
            ['^0.1', '0.1.2'],
            ['^1.2', '1.4.2'],
            ['^1.2 ^1', '1.4.2'],
            ['^1.2.3-alpha', '1.2.3-pre'],
            ['^1.2.0-alpha', '1.2.0-pre'],
            ['^0.0.1-alpha', '0.0.1-beta'],
        ]
        for pattern, version in data:
            pattern = Range(pattern)
            self.assertIn(
                version,
                pattern,
                msg='%s should be in %s' % (version, pattern)
            )

    def test_loose_range_matches(self):
        data = [
            ['1.2.3pre+asdf - 2.4.3-pre+asdf', '1.2.3'],
            ['1.2.3-pre+asdf - 2.4.3pre+asdf', '1.2.3'],
            ['1.2.3pre+asdf - 2.4.3pre+asdf', '1.2.3'],
            ['*', 'v1.2.3'],
            ['>=0.1.97', 'v0.1.97'],

            # node's semver doesn't consider these a loose range:
            ['~v0.5.4-pre', '0.5.5'],
            ['~v0.5.4-pre', '0.5.4'],
        ]
        for pattern, version in data:
            pattern = Range(pattern, loose=True)
            self.assertIn(
                version,
                pattern,
                msg='%s should be in %s' % (version, pattern)
            )

    def test_range_non_matches(self):
        data = [
            ['1.0.0 - 2.0.0', '2.2.3'],
            ['1.2.3+asdf - 2.4.3+asdf', '1.2.3-pre.2'],
            ['1.2.3+asdf - 2.4.3+asdf', '2.4.3-alpha'],
            ['^1.2.3+build', '2.0.0'],
            ['^1.2.3+build', '1.2.0'],
            ['^1.2.3', '1.2.3-pre'],
            ['^1.2', '1.2.0-pre'],
            ['>1.2', '1.3.0-beta'],
            ['<=1.2.3', '1.2.3-beta'],
            ['^1.2.3', '1.2.3-beta'],
            ['=0.7.x', '0.7.0-asdf'],
            ['>=0.7.x', '0.7.0-asdf'],
            ['1.0.0', '1.0.1'],
            ['>=1.0.0', '0.0.0'],
            ['>=1.0.0', '0.0.1'],
            ['>=1.0.0', '0.1.0'],
            ['>1.0.0', '0.0.1'],
            ['>1.0.0', '0.1.0'],
            ['<=2.0.0', '3.0.0'],
            ['<=2.0.0', '2.9999.9999'],
            ['<=2.0.0', '2.2.9'],
            ['<2.0.0', '2.9999.9999'],
            ['<2.0.0', '2.2.9'],
            ['>=0.1.97', '0.1.93'],
            ['0.1.20 || 1.2.4', '1.2.3'],
            ['>=0.2.3 || <0.0.1', '0.0.3'],
            ['>=0.2.3 || <0.0.1', '0.2.2'],
            ['2.x.x', '1.1.3'],
            ['2.x.x', '3.1.3'],
            ['1.2.x', '1.3.3'],
            ['1.2.x || 2.x', '3.1.3'],
            ['1.2.x || 2.x', '1.1.3'],
            ['2.*.*', '1.1.3'],
            ['2.*.*', '3.1.3'],
            ['1.2.*', '1.3.3'],
            ['1.2.* || 2.*', '3.1.3'],
            ['1.2.* || 2.*', '1.1.3'],
            ['2', '1.1.2'],
            ['2.3', '2.4.1'],
            ['~2.4', '2.5.0'],  # >= 2.4.0 < 2.5.0
            ['~2.4', '2.3.9'],
            ['~>3.2.1', '3.3.2'],  # >= 3.2.1 < 3.3.0
            ['~>3.2.1', '3.2.0'],  # >= 3.2.1 < 3.3.0
            ['~1', '0.2.3'],  # >= 1.0.0 < 2.0.0
            ['~>1', '2.2.3'],
            ['~1.0', '1.1.0'],  # >= 1.0.0 < 1.1.0
            ['<1', '1.0.0'],
            ['>=1.2', '1.1.1'],
            ['=0.7.x', '0.8.2'],
            ['>=0.7.x', '0.6.2'],
            ['<0.7.x', '0.7.2'],
            ['<1.2.3', '1.2.3-beta'],
            ['=1.2.3', '1.2.3-beta'],
            ['>1.2', '1.2.8'],
            ['^1.2.3', '2.0.0-alpha'],
            ['^1.2.3', '1.2.2'],
            ['^1.2', '1.1.9'],
            ['^1.2.3', '2.0.0-pre'],
        ]
        for pattern, version in data:
            pattern = Range(pattern)
            self.assertNotIn(
                version,
                pattern,
                msg='%s should not be in %s' % (version, pattern)
            )

    def test_loose_range_non_matches(self):
        data = [
            ['1', '1.0.0beta'],
            ['<1', '1.0.0beta'],
            ['< 1', '1.0.0beta'],
            ['>=0.1.97', 'v0.1.93'],
            ['1', '2.0.0beta'],
            ['*', 'v1.2.3-foo'],

            # node's semver doesn't consider these a loose range:
            ['~v0.5.4-beta', '0.5.4-alpha'],
        ]
        for pattern, version in data:
            pattern = Range(pattern, loose=True)
            self.assertNotIn(
                version,
                pattern,
                msg='%s should not be in %s' % (version, pattern)
            )

    def test_invalid(self):
        data = [
            'blerg',
            'git+https://user:password0123@github.com/foo',

            '>=1 a',
            '? >=1',
        ]
        for pattern in data:
            with self.assertRaises(ValueError, msg='Pattern should be invalid %s' % pattern):
                Range(pattern, loose=True)

    def test_min_satisfying(self):
        data = [
            [['1.2.3', '1.2.4'], '1.2', '1.2.3'],
            [['1.2.4', '1.2.3'], '1.2', '1.2.3'],
            [['1.2.3', '1.2.4', '1.2.5', '1.2.6'], '~1.2.3', '1.2.3'],
        ]
        for versions, pattern, expected in data:
            pattern = Range(pattern)
            self.assertEqual(pattern.lowest_version(versions), expected)

        data = [
            [
                ['1.1.0', '1.2.0', '1.2.1', '1.3.0', '2.0.0b1', '2.0.0b2', '2.0.0b3', '2.0.0', '2.1.0'],
                '~2.0.0', '2.0.0'
            ],
        ]
        for versions, pattern, expected in data:
            pattern = Range(pattern, loose=True)
            self.assertEqual(pattern.lowest_version(versions), expected)

    def test_max_satisfying(self):
        data = [
            [['1.2.3', '1.2.4'], '1.2', '1.2.4'],
            [['1.2.4', '1.2.3'], '1.2', '1.2.4'],
            [['1.2.3', '1.2.4', '1.2.5', '1.2.6'], '~1.2.3', '1.2.6'],
        ]
        for versions, pattern, expected in data:
            pattern = Range(pattern)
            self.assertEqual(pattern.highest_version(versions), expected)

        data = [
            [
                ['1.1.0', '1.2.0', '1.2.1', '1.3.0', '2.0.0b1', '2.0.0b2', '2.0.0b3', '2.0.0', '2.1.0'],
                '~2.0.0', '2.0.0'
            ],
        ]
        for versions, pattern, expected in data:
            pattern = Range(pattern, loose=True)
            self.assertEqual(pattern.highest_version(versions), expected)


class CodeStyleTestCase(unittest.TestCase):
    def test_code_style(self):
        try:
            subprocess.check_output(['python', '-m', 'flake8'])
        except subprocess.CalledProcessError as e:
            self.fail('Code style checks failed\n\n%s' % e.output.decode('utf-8'))
