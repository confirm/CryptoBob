'''
CryptoBob trade plan module.
'''

__all__ = (
    'TradePlan',
)

from datetime import timedelta
from logging import getLogger
from zlib import crc32

LOGGER = getLogger(__name__)


class TradePlan:
    '''
    The trade plan class.

    :param binance.client.Client client: The binance client
    :param str pair: The trading pair
    :param float amount: The amount
    :param dict schedule: The schedule
    '''

    configuration_attribute = 'trade_plans'

    def __init__(self, client, pair, amount, schedule):
        self.client = client
        self.pair   = pair
        self.amount = amount
        self.delta  = timedelta(**schedule)

    def __str__(self):
        '''
        The informal string version of the object.

        :return: The informal string version
        :rtype: str
        '''
        return self.pair

    def __repr__(self):
        '''
        The official string version of the object.

        :return: The informal string version
        :rtype: str
        '''
        return f'<{self.__class__.__name__}: {self.pair}>'

    def __call__(self):
        '''
        Check if the trade has to be executed, then execute it.
        '''
        LOGGER.debug('Evaluating %r', self)
