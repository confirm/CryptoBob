'''
CryptoBob withdrawal module.
'''

__all__ = (
    'Withdrawal',
)

from logging import getLogger

LOGGER = getLogger(__name__)


class Withdrawal:
    '''
    The withdrawal class.

    :param runner.Runner runner: The runner
    :param str asset: The asset ID
    :param float threshold: The threshold when the withdrawal should be triggered
    :param str key: The address key (must be configured on Kraken)
    :param str address: The address to which the asset should be transferred
    :param amount: The amount
    :type amount: None or float
    '''

    configuration_attribute = 'withdrawals'

    def __init__(self, runner, asset, threshold, key, address, amount=None):  # pylint: disable=too-many-arguments
        self.runner    = runner
        self.asset     = asset
        self.threshold = threshold
        self.key       = key
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
        Check if the withdrawal threshold is exceeded, then automatically
        withdraw the asset to the defined address.
        '''
        LOGGER.debug('Evaluating %r', self)

        asset     = self.asset
        threshold = self.threshold
        amount    = self.amount or 0.0
        address   = self.address
        key       = self.key

        balance = float(self.runner.client.balance.get(asset) or 0.0)
        LOGGER.debug('%s balance is %f, configured withdrawal threshold is %f',
                     asset, balance, threshold)

        if balance < threshold:
            LOGGER.debug('%s threshold not exceeded, skipping withdrawal', asset)
            return

        withdraw_amount = min(amount or balance, balance)

        LOGGER.info('Initiating withdrawal of %f %s to %s', withdraw_amount, asset, address)
        if not self.runner.config.get('test', False):
            self.runner.client.request(
                'Withdraw',
                asset=asset,
                key=key,
                address=address,
                amount=withdraw_amount,
            )
