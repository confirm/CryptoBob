CryptoBob
=========

CryptoBob is a radically simple crypto currency bot, which interacts with [Kraken](https://kraken.com) and…

- … automatically buys crypto currencies on a recurring basis
- … automatically withdraws crypto currencies when a threshold is reached

_CryptoBob_ is your perfect little sidekick, when you want to automate the purchase and storage of crypto currencies on your hardware wallet / ledger.
Of course there are services out there doing this, but usually Kraken has much better fees than those services, and a much better selection of crypto ;)

Installation
============

Install the package via PyPi:

```
pip3 install cryptobob
```

Install the package from source:

```
pip3 install cryptobob@git+https://git.confirm.ch/confirm/cryptobob.git
```

Usage
=====

The usage of ``cryptobob`` is quite simple:

```
usage: cryptobob [-h] [-c CONFIG] [-s] [-v] {run,buy,assets,otp}

CryptoBob - The bot which buys & withdraws crypto automatically.

positional arguments:
  {run,buy,assets,otp}        action to execute

options:
  -h, --help                  show this help message and exit
  -c CONFIG, --config CONFIG  path to the CryptoBob config
  -s, --simple                enable simple logging format (e.g. for systemd)
  -v, --verbose               enable verbose logging mode (repeat to increase verbosity, up to -vvv)
```

To display all assets listed on Kraken, you can run:

```bash
cryptobob assets
```

To run _CryptoBob_, you can simply execute:

```bash
cryptobob run -vv
```

To (force) buy / execute the configured trade plans, you can run:

```bash
cryptobob buy -vv
```

In case you configured OTP for your API key and want to get a one-time code, you can run:

```bash
cryptobob otp
```

Please note you've to configure _CryptoBob_ accordingly.  
Check out the next section for the configuration.

Configuration
=============

By default, _CryptoBob_ is searching its configuration file under `~/.cryptobob.yml`.  
Feel free to change the configuration file path by specifying the `-c` or `--config` CLI flag.

You can find an example configuration in the _CryptoBob_ repository called [`cryptobob.yml`](cryptobob.yml).

__IMPORTANT:__ The configuration file contains sensitive informations. Make sure you set the permissions right!

Runtime data
============

Please note _CryptoBob_ doesn't store any runtime data or alike on your system, since it will always check in with Kraken directly.

For example, when you configure an interval of buying a certain asset, _CryptoBob_ will always check the order history, to find the last executed order.
Given the retreived order timestamp, _CryptoBob_ decides to open new orders based on your configuration.

Of course, only orders initiated by _CryptoBob_ will be queried for the timestamps (achieved via [`userref` on `ClosedOrders`](https://docs.kraken.com/rest/#tag/Account-Data/operation/getClosedOrders)).
