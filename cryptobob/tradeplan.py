'''
CryptoBob trade module.
'''

__all__ = (
    'TradePlan',
)

from datetime import timedelta
from logging import getLogger

LOGGER = getLogger(__name__)


class TradePlan:
    '''
    The trading class.

    :param binance.client.Client client: The binance client
    :param str symbol: The trading symbol
    :param float quantity: The quantity
    :param dict schedule: The schedule
    '''

    def __init__(self, client, symbol, quantity, schedule):
        self.client   = client
        self.symbol   = symbol
        self.quantity = quantity
        self.delta    = timedelta(**schedule)

    def __str__(self):
        '''
        The informal string version of the object.

        :return: The informal string version
        :rtype: str
        '''
        return self.symbol

    def __repr__(self):
        '''
        The official string version of the object.

        :return: The informal string version
        :rtype: str
        '''
        return f'<{self.__class__.__name__}: {self.symbol}>'

    def __call__(self):
        '''
        Check if the trade has to be executed, then execute it.
        '''
        LOGGER.debug('Evaluating %r', self)
