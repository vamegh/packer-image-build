#!/usr/bin/env python3

### (c) Vamegh Hedayati LGPL License please read the License file for more info.
from setuptools import setup

setup(
    name='get_jenkins_master',
    version='0.0.1',
    description='A tool to get the jenkins master ip address - used in conjunction with systemd to restart jenkins agent on master changes',
    author='Vamegh Hedayati',
    author_email='gh_vhedayati@ev9.io',
    url='https://github.com/vamegh',
    include_package_data=True,
    packages=['build_libs'],
    scripts=[
        'bin/get_jenkins_master',
    ],
    package_data={'build_libs': ['README.md'], }
)