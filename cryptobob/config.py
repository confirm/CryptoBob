'''
CryptoBob config.
'''

__all__ = (
    'Config',
)

from logging import getLogger

from yaml import safe_load

from .exceptions import ConfigError

LOGGER = getLogger(__name__)


class Config:  # pylint: disable=too-few-public-methods
    '''
    Configuration class of CryptoBob.

    It basically reads the configuration settings from a simple YAML file,
    then stores it internally. The YAML parameters can then be accessed via
    instance attributes. If a parameter wasn't found, an exception is
    raised.

    :param pathlib.Path path: The path to the config
    '''

    def __init__(self, path):
        self.data = {}
        self.path = path

        self.load()

    def __getattr__(self, attr):
        '''
        Get attribute method to fetch config instances.
        '''
        try:
            return self.data[attr]
        except KeyError as ex:
            raise ConfigError(f'Missing configuration property {ex}') from ex

    def load(self):
        '''
        Load the configuration file.
        '''
        LOGGER.debug('Loading configuration from %r', str(self.path))

        path = self.path.expanduser()
        with path.open('r', encoding='utf-8') as file:
            self.data = safe_load(file)
