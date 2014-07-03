#!/usr/bin/env python

from distutils.core import setup
from commands import getoutput

version = getoutput('git describe --always') or '1.0'

setup(name='unifi',
      version=version,
      description='API towards Ubiquity Networks UniFi controller',
      author='Jakob Borg',
      author_email='jakob@nym.se',
      url='https://github.com/calmh/unifi-api',
      packages=['unifi'],
      scripts=['unifi-low-snr-reconnect', 'unifi-ls-clients', 'unifi-save-statistics'],
      classifiers=['Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Libraries',
          'Topic :: System :: Networking']
     )
