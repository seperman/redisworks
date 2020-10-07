import os
from setuptools import setup

# if you are not using vagrant, just delete os.link directly,
# The hard link only saves a little disk space, so you should not care
if os.environ.get('USER', '') == 'vagrant':
    del os.link

try:
    with open('README.txt') as file:
        long_description = file.read()
except:
    long_description = "Pythonic Redis Client."

setup(name='redisworks',
      version='0.3.0',
      description='Pythonic Redis Client.',
      url='https://github.com/seperman/redisworks',
      download_url='https://github.com/seperman/redisworks/tarball/master',
      author='Seperman',
      author_email='sep@zepworks.com',
      license='MIT',
      packages=['redisworks'],
      zip_safe=False,
      test_suite="tests",
      long_description=long_description,
      install_requires=[
          'redis',
          'dotobject'
      ],
      tests_require=['fakeredis==1.4.3', 'pytest==6.1.1'],
      classifiers=[
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Topic :: Software Development",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: Implementation :: PyPy",
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: MIT License"
      ],
      )
