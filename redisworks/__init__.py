import logging
from .redisworks import Root  # NOQA

__version__ = '0.3.0'


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)8s %(message)s')
