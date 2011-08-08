from setuptools import setup, find_packages

setup(name='timak',
    version=".".join(map(str, __import__("timak").__version__)),
    description='Timelines (activity streams) backed by Riak',
    author='Brett Hoerner',
    author_email='brett@bretthoerner.com',
    url='http://github.com/bretthoerner/timak',
    packages=find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
    license="Apache License (2.0)",
)
