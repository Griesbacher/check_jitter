# check_jitter
Poor man's check_jitter. Measures the jitter by ping or other external tools.
**Works with python 2 and 3**
##Usage
``` bash
usage: check_jitter.py [-h] [--tool [TOOL]] [-w [WARN]] [-c [CRIT]]
                       [--retries [RETRIES]]
                       host

Poor man's check_jitter. Measures the jitter by ping or other external tools.
Available @ https://github.com/Griesbacher/check_jitter - Philip Griesbacher
Pings the target twice with a delay of one second. Returns the difference
between the rtt. If one ping did not success it will wait a second and try
again.

positional arguments:
  host                 Target Host

optional arguments:
  -h, --help           show this help message and exit
  --tool [TOOL]        External tool to measure the jitter. Supported: ping.
                       Default: ping.
  -w [WARN]            Warning threshold
  -c [CRIT]            Critical threshold
  --retries [RETRIES]  Retires for lost ping package. Default: 3
```
###Example
``` bash
$ python check_jitter.py  -c 20 -w 5 baidu.com
WARNING - baidu.com: 7ms | 'baidu.com'=7ms;5;20;0;
```
