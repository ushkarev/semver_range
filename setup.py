import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

root_path = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))
with open(os.path.join(root_path, 'README.rst')) as readme:
    README = readme.read()

setup(
    name='semver_range',
    version='0.0.1',
    author='Igor Ushkarev',
    url='https://github.com/ushkarev/semver_range',
    py_modules=['semver_range'],
    license='MIT',
    description='Python package that mimics npm’s “semver” package',
    long_description=README,
    keywords='semver,semantic-versioning,semver_range',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    tests_require=['flake8'],
    test_suite='tests',
)
