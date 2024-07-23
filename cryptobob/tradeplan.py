'''
CryptoBob trade plan module.
'''

__all__ = (
    'TradePlan',
)

from datetime import timedelta
from logging import getLogger
from struct import pack, unpack
from time import time
from zlib import crc32

from .exceptions import ResponseError, TradePlanError

LOGGER = getLogger(__name__)


class TradePlan:
    '''
    The trade plan class.

    :param runner.Runner runner: The runner
    :param str pair: The trading pair
    :param float amount: The amount
    :param dict interval: Theinterval
    '''

    configuration_attribute = 'trade_plans'

    def __init__(self, runner, pair, amount, interval):
        self.runner      = runner
        self.pair        = pair
        self.amount      = amount
        self.interval    = timedelta(**interval)
        self.last_order  = None
        self.last_failed = None

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

        self.ensure_no_open_orders()

        self.fetch_last_closed_order()

        should_open, reason = self.validate_order_opening()
        LOGGER.debug('Order opening decision:')
        LOGGER.debug('    Decision: %r', should_open)
        LOGGER.debug('    Reason:   %r', reason)

        if should_open:
            self.open_order()

    @property
    def userref(self):
        '''
        The custom userref ID for this trade plan.

        :return: The userref
        :rtype: 32-bit int
        '''
        # CRC32 in Python 3 always retruns unsigned.
        unsigned = crc32(f'{self.runner.client.api_key}:{self.pair}'.encode('utf-8'))

        # Convert unsigned to signed, as Kraken requires a signed 32-bit integer.
        return unpack('i', pack('I', unsigned))[0]

    def ensure_no_open_orders(self):
        '''
        Ensure there are no open orders for this trade plan.

        :raises TradePlanError: When there are open orders
        '''
        if self.runner.client.request('OpenOrders', userref=self.userref)['open']:
            raise TradePlanError(f'There are still open orders for {self!r}, skipping…')

    def fetch_last_closed_order(self):
        '''
        Get the last closed order for this trade plan.
        '''
        orders = self.runner.client.request('ClosedOrders', userref=self.userref)['closed']

        try:
            self.last_order = sorted(orders.values(),
                                     key=lambda order: order['closetm'], reverse=True)[0]
            LOGGER.debug('Last closed order is %r', self.last_order)
        except IndexError:
            self.last_order = None
            LOGGER.debug('No last closed order found yet')

    def validate_order_opening(self):
        '''
        Validate the opening of a new order.

        :return: The decision & reason
        :rtype: tuple(bool, str)

        :raises TradePlanError: When an unexpected status is retreived
        '''
        LOGGER.debug('Validating order execution for %r', self)

        now            = int(time())
        last_failed    = self.last_failed
        interval       = self.interval.total_seconds()

        last_order = self.last_order
        status     = last_order['status'] if last_order else ''
        timestamp  = last_order['closetm'] if last_order else 0

        # Last opening failed without creating order, validate retry.
        if last_failed:
            return self.validate_retry(timestamp=last_failed, status='failed opening')

        # First time.
        if not last_order:
            return True, 'No existing order found yet'

        # Sanity check.
        if status not in ('closed', 'canceled', 'expired'):
            raise TradePlanError(f'Unexpected closed order status {status} for {self!r}')

        # Trade plan interval exceeded, regardless of status.
        if now >= timestamp + interval:
            return True, 'Trade plan interval exceeded'

        # Order normally closed as expected, but trade plan interval not exceeded yet.
        if status == 'closed':
            return False, 'Trade plan interval not exceeded yet'

        # Last abnormally closed, validate retry.
        return self.validate_retry(timestamp=timestamp, status=status)

    def validate_retry(self, timestamp, status):
        '''
        Validate retry for the opening of a new order.

        :param int timestamp: The timestamp of the last failure
        :param str status: The status

        :return: The decision & reason
        :rtype: tuple(bool, str)

        :raises TradePlanError: When an unexpected status is retreived
        '''
        now            = int(time())
        retry_interval = self.runner.config.retry_interval * 60
        retry_timeout  = self.runner.config.retry_timeout * 60

        if now > timestamp + retry_timeout:
            return False, f'Last order {status}, and retry timeout exceeded'

        # Retry interval exceeded.
        if now >= timestamp + retry_interval:
            LOGGER.warning('Last %r order %s, retrying now…', self, status)
            return True, f'Last order {status}, but retry interval exceeded'

        # Retry interval not exceeded yet.
        return False, f'Last order {status}, but retry interval not exceeded yet'

    def open_order(self):
        '''
        Open a new order.
        '''
        LOGGER.info('Opening new market order for %r with quote currency amount of %f',
                    self, self.amount)

        self.last_failed = None

        try:

            self.runner.client.request(
                'AddOrder',
                pair=self.pair,
                userref=self.userref,
                volume=self.amount,
                oflags='viqc',          # order volume expressed in quote currency
                ordertype='market',
                type='buy',
                timeinforce='GTC',
                validate=bool(self.runner.config.get('test', False)),
            )

        except ResponseError as ex:
            self.last_failed = time()
            LOGGER.warning('Opening order for %r failed with reason «%s»', self, str(ex))
