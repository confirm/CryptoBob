'''
CryptoBob withdrawl module.
'''

__all__ = (
    'Withdrawl',
)

from logging import getLogger

LOGGER = getLogger(__name__)


class Withdrawl:
    '''
    The withdrawl class.

    :param binance.client.Client client: The binance client
    :param str asset: The asset ID
    :param float threshold: The threshold when the withdrawl should be triggered
    :param str address: The address to which the withdrawl should be sent
    :param amount: The amount
    :type amount: None or float
    '''

    configuration_attribute = 'withdrawls'

    def __init__(self, client, asset, threshold, address, amount=None):  # pylint: disable=too-many-arguments
        self.client    = client
        self.asset     = asset
        self.threshold = threshold
        self.address   = address
        self.amount    = amount
        self.balance   = 0.0

    def __str__(self):
        '''
        The informal string version of the object.

        :return: The informal string version
        :rtype: str
        '''
        return self.asset

    def __repr__(self):
        '''
        The official string version of the object.

        :return: The informal string version
        :rtype: str
        '''
        return f'<{self.__class__.__name__}: {self.asset}>'

    def __call__(self):
        '''
        Check if the withdrawl threshold is exceeded, then automatically
        withdraw the asset to the defined address.
        '''
        LOGGER.debug('Evaluating %r', self)
