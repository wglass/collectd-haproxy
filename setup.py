from setuptools import setup, find_packages

from collectd_haproxy import __version__


classifiers = []
with open("classifiers.txt") as fd:
    classifiers = fd.readlines()


setup(
    name="collectd-haproxy",
    version=__version__,
    description="HAProxy stats plugin for collectd.",
    author="William Glass",
    author_email="william.glass@gmail.com",
    url="http://github.com/wglass/collectd-haproxy",
    license="MIT",
    classifiers=classifiers,
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=[],
    tests_require=[
        "nose",
        "mock",
        "coverage",
        "flake8",
    ],
)
