'''
CryptoBob runner.
'''

__all__ = (
    'Runner',
)

from logging import getLogger
from time import sleep

from .exceptions import ConfigError
from .kraken import KrakenClient
from .tradeplan import TradePlan

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

    def __call__(self):
        '''
        Run the runner by executing all test cases.
        '''
        LOGGER.info('Starting CryptoBob runner')

        self.init_client()
        self.init_trades()

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

    def init_trades(self):
        '''
        Initialise the trades.
        '''
        LOGGER.debug('Initialising trade plans')

        self.trade_plans = []

        for trade_plan in self.config.trade_plans:
            LOGGER.debug('Found trade plan configuration %r', trade_plan)
            self.trade_plans.append(TradePlan(client=self.client, **trade_plan))

    def start_cycle(self):
        '''
        Start the runner cycle.
        '''
        interval = self.config.interval * 60

        while True:
            LOGGER.debug('Starting new runner cycle')

            self.client.assert_online_status()

            for trade_plan in self.trade_plans:
                trade_plan()

            LOGGER.debug('Runner cycle finished, sleeping for %d seconds', interval)
            sleep(interval)
