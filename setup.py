from setuptools import setup, find_packages


version = "0.1.1"


setup(name='timak',
    version=version,
    description='Timelines (activity streams) backed by Riak',
    author='Brett Hoerner',
    author_email='brett@bretthoerner.com',
    url='http://github.com/bretthoerner/timak',
    packages=find_packages(),
    test_suite='unittest2.collector',
    install_requires=['riak'],
    tests_require=['unittest2'],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
    license="Apache License (2.0)",
)
