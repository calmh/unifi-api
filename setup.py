#!/usr/bin/env python

from distutils.core import setup
import sys

if sys.version_info[0] == 2:
    from commands import getoutput
elif sys.version_info[0] == 3:
    from subprocess import getoutput


version = getoutput('git describe --always') or '1.0'

setup(name='unifi',
      version=version,
      description='API towards Ubiquity Networks UniFi controller',
      author='Jakob Borg',
      author_email='jakob@nym.se',
      url='https://github.com/calmh/unifi-api',
      packages=['unifi'],
      scripts=['unifi-low-snr-reconnect', 'unifi-ls-clients', 'unifi-save-statistics', 'unifi-log-roaming'],
      classifiers=['Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Libraries',
          'Topic :: System :: Networking']
     )
