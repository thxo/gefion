#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Flask', 'Flask-HTTPAuth', 'Flask-SQLAlchemy', 'python-telegram-bot',
    'PyYAML', 'requests', 'retrying', 'rq', 'rq-scheduler'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(name='gefion',
      version='0.0.1',
      description="A distributed server monitoring solution.",
      long_description=readme + '\n\n' + history,
      author="Howard Xiao",
      author_email='hxiao+scm@dargasea.com',
      url='https://github.com/och/gefion',
      packages=[
          'gefion',
      ],
      package_dir={'gefion':
                   'gefion'},
      include_package_data=True,
      install_requires=requirements,
      license="BSD license",
      zip_safe=False,
      keywords='gefion',
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
      ],
      test_suite='tests',
      tests_require=test_requirements)
