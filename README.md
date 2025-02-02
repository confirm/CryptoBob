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

Linux service
-------------

_CryptoBob_ can also be run as Linux service, for example via `systemd`.

To use _CryptoBob_ as service, it's recommended to create a dedicated user, or to use your personal user for it.  
Creating a new Linux user can be achieved as `root` by running these commands:

```bash
# Create new POSIX group
groupadd -g 666 cyrptobob

# Create new POSIX user
useradd -d /home/cryptobob -m -g 666 -u 666 cryptobob
```

Then install _CryptoBob_ in a dedicated [Python venv](https://docs.python.org/3/library/venv.html) by running these commands:

```bash
# Change to new cryptobob user.
su - cryptobob

# Create new venv and activate it.
python3 -mvenv ~/.venv
source .venv/bin/activate

# Install CryptoBob
pip3 install cryptobob
```

The user needs to have access to the configuration file, documented in the [Configuration chapter](#Configuration).

Is your configuration ready and _CryptoBob_ installed, you can use the [example systemd service unit](example/cryptobob.service) to configure, start, and enable a [systemd service](https://wiki.debian.org/systemd/Services):

```bash
# Download systemd service unit.
curl -Lo /etc/systemd/system/cryptobob.service https://raw.githubusercontent.com/confirm/CryptoBob/master/example/cryptobob.service

# Reload systemd daemon
systemctl daemon-reload

# Start and enable service
systemctl enable cryptobob
systemctl start cryptobob
```

__HINT__: Please note that if you've updated the `cryptobob.service` file, you need to run `systemctl daemon-reload` again.

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

You can find an [example configuration](example/cryptobob.yml) in the _CryptoBob_ repository.

__IMPORTANT:__ The configuration file contains sensitive informations. Make sure you set the permissions right!

Runtime data
============

Please note _CryptoBob_ doesn't store any runtime data or alike on your system, since it will always use the Kraken order history as a reference for upcoming orders.

For example, when _CryptoBob_ buys a certain asset on Kraken, it will open a new buy order. That buy order is then submitted, executed, and stored on Kraken.
When _CryptoBob_ then runs again, it will retrieve the last executed order for certain asset from Kraken, compare its order timestamp with your configured interval, and checks if enough time has passed to open another buy oder.

Of course, only orders initiated by _CryptoBob_ will be queried for the timestamps (achieved via [`userref` on `ClosedOrders`](https://docs.kraken.com/rest/#tag/Account-Data/operation/getClosedOrders)).

