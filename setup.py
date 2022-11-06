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


def get_reqs(filename):
    with open(filename, "r") as reqs_file:
        reqs = reqs_file.readlines()
        reqs = list(map(lambda x: x.replace('==', '>='), reqs))
    return reqs


reqs = get_reqs("requirements.txt")


setup(name='redisworks',
      version='0.4.0',
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
      install_requires=reqs,
      classifiers=[
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Topic :: Software Development",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "Programming Language :: Python :: Implementation :: PyPy",
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License"
      ],
      )
