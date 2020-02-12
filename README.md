# PythonZeroconfTools

Cross-platform utility scripts for Zeroconf.

## Installation and Setup

The `zeroconf_detect.py` script uses the Python `zeroconf` package for convenience (the `zeroconf_register.py` script does not); this package can be installed using `pip3`:

```
pip3 install zeroconf
```

## Example service registration using `zeroconf_register.py`

To register a Zeroconf service, use the `zeroconf_register.py` script. Running this script with no parameters on the command line provides basic usage instructions:

```
$ python3 zeroconf_register.py 

Usage:

zeroconf_register.py svc_name [svc_type=x] [svc_port=x] [svc_txt=x]

Default values for optional parameters:

svc_type : _http._tcp
svc_port : 666
svc_txt : None

$
```

For a simple example, we can register a service called `test` providing HTTP over TCP; when run on macOS, this results int he following:

```
$ python3 zeroconf_register.py test
{'svc_type': '_john._tcp', 'svc_port': '666', 'svc_txt': None, 'svc_name': 'test'}
Platform "Darwin" assumed to be macOS, using ['dns-sd', '-R', 'test', '_john._tcp', 'local', '666'] ...```
```

At this point, the script will keep running until terminated. This should not be a problem, as it uses very little resources.

A more complicated example may involve a custom service type over UDP on port 12233, along with some information stored as a DNS TXT entry:

```
$ python3 zeroconf_register.py test svc_type=_custom._udp  svc_port=12233 svc_txt="key=value"
{'svc_type': '_custom._udp', 'svc_port': '12233', 'svc_txt': 'key=value', 'svc_name': 'test'}
Platform "Darwin" assumed to be macOS, using ['dns-sd', '-R', 'test', '_custom._udp', 'local', '12233', 'key=value'] ...
```

## Example service detection using `zeroconf_detect.py`

To detect Zeroconf services, use the `zeroconf_detect.py` script. Running this script with no parameters on the command line provides basic usage instructions:


```
$ python3 zeroconf_detect.py

Usage:

zeroconf_detect.py svc_type [heartbeat=x]

Example:

zeroconf_detect.py _http_.tcp heartbeat=1.5

Default values for optional parameters:

heartbeat : 2.0

$
```

To detect e.g. services for HTTP over TCP:

```
$ python3 zeroconf_detect.py _http._tcp
```

At this point, the script will keep running until terminated. This should not be a problem, as it uses very little resources.

Registration of new services, or removal of existing services, will trigger printing of the current service list.
