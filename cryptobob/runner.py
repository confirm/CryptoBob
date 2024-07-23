'''
CryptoBob runner.
'''

__all__ = (
    'Runner',
)

from logging import getLogger
from time import sleep

from .exceptions import ConfigError, TradePlanError
from .kraken import KrakenClient
from .tradeplan import TradePlan
from .withdrawl import Withdrawl

LOGGER = getLogger(__name__)


class Runner:
    '''
    The CryptoBob runner class which initiates all the trades.
    '''

    def __init__(self, config):
        '''
        Constructor.
        '''
        self.config      = config
        self.client      = None
        self.trade_plans = []
        self.withdrawls  = []

    def __call__(self):
        '''
        Run the runner by executing all test cases.
        '''
        LOGGER.info('Starting CryptoBob runner')

        self.init_client()
        self.init_trade_plans()
        self.init_withdrawls()

        self.start_cycle()

    def init_client(self):
        '''
        Initialise the client.
        '''
        LOGGER.debug('Initialising client')

        try:
            otp_uri = self.config.otp_uri
        except ConfigError:
            otp_uri = None

        kwargs = {
            'api_key': self.config.api_key,
            'private_key': self.config.private_key,
            'otp_uri': otp_uri
        }

        self.client = KrakenClient(**kwargs)

    def init_configuration_instances(self, klass):
        '''
        Look up defined instances in the configuration, then automatically
        initialise them to Python instances, so that the runner can access them
        later in the run cycle.

        The passed :param:`klass` class defines the attribute name of the
        configuration. The defined keyword arguments are then automatically
        passed to the class constructor, and the instantiated object is then
        added to the runner.

        :param class klass: The class

        :raises ConfigError: When there's configuration / kwarg error
        '''
        name = klass.__name__
        attr = klass.configuration_attribute

        LOGGER.debug('Initialising %s instances', name)

        items = []
        setattr(self, attr, items)

        for item in getattr(self.config, attr):
            LOGGER.debug('Initialising %s instance for configuration %r', name, item)

            try:
                items.append(klass(runner=self, **item))
            except TypeError as ex:
                error = f'{name} configuration {item!r} misconfigured, got «{ex}»'
                raise ConfigError(error) from ex

    def init_trade_plans(self):
        '''
        Initialise the trade plans.
        '''
        self.init_configuration_instances(TradePlan)

    def init_withdrawls(self):
        '''
        Initialise the withdrawls.
        '''
        self.init_configuration_instances(Withdrawl)

    def start_cycle(self):
        '''
        Start the runner cycle.
        '''
        interval = self.config.interval * 60

        while True:
            LOGGER.debug('========== CYCLE START')
            LOGGER.debug('Starting new runner cycle')

            self.client.assert_online_status()

            for trade_plan in self.trade_plans:
                try:
                    trade_plan()
                except TradePlanError as ex:
                    LOGGER.warning(ex)

            self.client.update_balance()

            for withdrawl in self.withdrawls:
                withdrawl()

            LOGGER.debug('Runner cycle finished, sleeping for %d seconds', interval)
            LOGGER.debug('========== CYCLE FINISH')
            sleep(interval)
