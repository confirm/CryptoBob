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

    public_methods = [
        'SystemStatus',
    ]

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

    def _prepare_request(self, api_method, data=None):
        '''
        Prepare the HTTP request and return the url & data.

        :param str api_method: The API method
        :param data: The POST data
        :type data: None or dict

        :return: The URL, urlencoded data, and headers
        :rtype: dict
        '''
        public  = api_method in self.public_methods

        endpoint = '/0'
        endpoint += '/public/' if public else '/private/'
        endpoint += api_method

        url  = f'https://{self.api_host}{endpoint}'

        headers = {
            'User-Agent': 'CryptoBob',
        }

        if not public:
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

    def request(self, api_method, data=None):
        '''
        Make a request to the Kraken API.

        :param str api_method: The API method
        :param data: The POST data
        :type data: None or dict

        :return: The response result
        :rtype: dict

        :raises ResponseError: When there was an error in the response
        '''
        kwargs  = self._prepare_request(api_method=api_method, data=data)
        request = Request(**kwargs)

        with urlopen(request) as response:
            response_data  = load(response)

            LOGGER.debug('Reponse is %r', response_data)

            response_error = response_data.get('error')
            if response_error:
                raise ResponseError(', '.join(response_error))

        return response_data['result']

    def assert_online_status(self):
        '''
        Assert that the exchange status is online (and not maintenance).

        :raises exceptions.StatusError: When system status isn't online
        '''
        LOGGER.debug('Asserting online system status')

        status = self.request('SystemStatus')['status']
        if status != 'online':
            raise StatusError(f'System status is {status!r}')
