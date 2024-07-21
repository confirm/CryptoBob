'''
CryptoBob Kraken module.
'''

__all__ = (
    'KrakenClient',
)

from base64 import b64decode, b64encode
from hashlib import sha256, sha512
from hmac import digest as hmac_digest
from json import load
from logging import getLogger
from time import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from pyotp import parse_uri as otp_parse_uri

from .exceptions import ResponseError, StatusError

LOGGER = getLogger(__name__)


class KrakenClient:
    '''
    The API client to talk to the Kraken REST API.

    :param str api_key: The API key retreived from Kraken
    :param str private_key: The private key retreived from Kraken
    :param otp_uri: The 2FA / OTP URI retreived from Kraken (optional)
    :type otp_uri: None or str
    '''

    api_host = 'api.kraken.com'

    def __init__(self, api_key, private_key, otp_uri=None):
        self.api_key     = api_key
        self.private_key = b64decode(private_key)
        self.otp_uri     = otp_uri

    def _sign_request(self, endpoint, data):
        '''
        Sign the HTTP request and return the new data string, as well as
        additional headers required for authentication.

        :param str endpoint: The API endpoint / path
        :param str data: The urlencoded POST data

        :return: The signed data & headers
        :rtype: tuple(str, list)
        '''
        # Prepare data.
        data = data or {}

        # Use UNIX timestamp as nonce and append it do the data.
        data['nonce'] = str(int(time() * 1000))

        # Add OTP if OTP is set
        if self.otp_uri:
            data['otp'] = otp_parse_uri(self.otp_uri).now()

        # URL-encode data.
        data_encoded = urlencode(data)

        # Create SHA256 hash of nonce & data.
        hash_sha256 = sha256(f'{data["nonce"]}{data_encoded}'.encode('utf-8')).digest()

        # Create SHA512 HMAC digest for endpoint & SHA256-hashed nonce & data.
        hmac_sha512 = hmac_digest(
            key=self.private_key,
            msg=endpoint.encode('utf-8') + hash_sha256,
            digest=sha512
        )

        # Create headers.
        headers = {
            'API-Key': self.api_key,
            'API-Sign': b64encode(hmac_sha512),
        }

        return data_encoded, headers

    def _prepare_request(self, action, private=True, data=None):
        '''
        Prepare the HTTP request and return the url & data.

        :param str action: The API action
        :param bool private: Flag for private or public endpoint
        :param data: The POST data
        :type data: None or dict

        :return: The URL, urlencoded data, and headers
        :rtype: dict
        '''
        endpoint = '/0'
        endpoint += '/private/' if private else '/public/'
        endpoint += action

        url  = f'https://{self.api_host}{endpoint}'

        headers = {
            'User-Agent': 'CryptoBob',
        }

        if private:
            data, additional_headers = self._sign_request(endpoint=endpoint, data=data)
            headers.update(additional_headers)

        LOGGER.debug('Request URL is %r', url)
        LOGGER.debug('Request POST data is %r', data)
        LOGGER.debug('Request HTTP headers %r', headers)

        kwargs = {
            'url': url,
            'headers': headers,
        }

        if data:
            kwargs['data'] = data.encode('utf-8')

        return kwargs

    def _request(self, **kwargs):
        '''
        Make a request to the Kraken API.

        Please refer to the :meth:`_prepare_request` method for the signature,
        resp. keyword arguments of this method.

        :param dict \\**kwargs: The keyword arguments
        '''
        kwargs  = self._prepare_request(**kwargs)
        request = Request(**kwargs)

        with urlopen(request) as response:
            response_data  = load(response)

            LOGGER.debug('Reponse is %r', response_data)

            response_error = response_data.get('error')
            if response_error:
                raise ResponseError(', '.join(response_error))

        return response_data['result']

    @property
    def status(self):
        '''
        The system status of the Kraken exchange.

        :return: The status
        :rtype: str
        '''
        return self._request(action='SystemStatus', private=False)['status']

    def assert_online_status(self):
        '''
        Assert that the exchange status is online (and not maintenance).

        :raises exceptions.StatusError: When system status isn't online
        '''
        LOGGER.debug('Asserting online system status')

        status = self.status
        if status != 'online':
            raise StatusError(f'System status is {status!r}')

    @property
    def balance(self):
        '''
        The account balance.

        :return: The balance
        :rtype: dict
        '''
        return self._request(action='Balance')
