import os
from distutils.core import setup

root = os.path.dirname(os.path.realpath(__file__))

setup(
    name='localdev',
    version='0.1.4',
    author='Cole Krumbholz',
    author_email='cole@brace.io',
    description='Turn-key DNS server and proxy for multi-domain development.',
    packages=['localdev'],
    install_requires=open(root+"/requirements.txt").read().splitlines(),
    long_description=open(root+"/README.md").read(),
    license='LICENSE',
    scripts=['scripts/localdev'],
)