import argparse
import platform
import re
import subprocess
import sys
import time

TRIES = 2


def ping(host):
    results = []
    for i in range(TRIES):
        measurement = None
        if platform.system() == "Windows":
            measurement = ping_exec(["ping", host, "-n", "1"], b'^\s+\w+\s=\s(\d+)(\w+),')
        elif platform.system() == "Linux":
            measurement = ping_exec(["ping", host, "-c", "1"], b'^rtt\smin/avg/max/mdev\s=\s(\d+\.?\d*).*?\s(\w+)$')
        if measurement is not None:
            results.append(measurement)
            if len(results) == 2:
                break
        time.sleep(1)
    if len(results) == 2:
        jitter = results[0] - results[1]
        if jitter < 0:
            return jitter * -1
        return jitter
    else:
        return None


def ping_exec(cmd, regex):
    output = exec_command(cmd)
    if output:
        match = re.search(regex, output, re.M)
        if match:
            duration = int(float(match.group(1)))
            if match.group(2) == "ms" or match.group(2) == b'ms':
                return duration
            elif match.group(2) == "s" or match.group(2) == b's':
                return duration * 1000
    return None


def exec_command(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output, err) = process.communicate()
    if err is None:
        exit_code = process.wait()
        if exit_code == 0:
            return output
    return None


def handle_args():
    parser = argparse.ArgumentParser(description="""Poor man\'s check_jitter.
Measures the jitter by ping or other external tools.
Available @ https://github.com/Griesbacher/check_jitter - Philip Griesbacher
Pings the target twice with a delay of one second. Returns the difference between the rtt.
If one ping did not success it will wait a second and try again.
""")
    parser.add_argument(dest='host',
                        type=str,
                        nargs=1,
                        help='Target Host')
    parser.add_argument('--tool',
                        dest='tool',
                        help='External tool to measure the jitter. Supported: ping. Default: ping.',
                        default='ping',
                        nargs="?",
                        type=str)
    parser.add_argument('-w',
                        dest='warn',
                        help='Warning threshold',
                        nargs="?",
                        type=str)
    parser.add_argument('-c',
                        dest='crit',
                        help='Critical threshold',
                        nargs="?",
                        type=str)
    parser.add_argument('--retries',
                        dest='retries',
                        help='Retires for lost ping package. Default: 3',
                        nargs="?",
                        default=3,
                        type=int)
    return parser.parse_args()


def handle_threshold(value, threshold):
    if threshold is "":
        return ""
    threshold = threshold.strip()
    m = re.search('^(@|~)?(\d*)(:)?(\d*)$', threshold, re.M)
    if not m:
        return "The given threshold is not valid: " + threshold
    else:
        if m.group(1) is None and m.group(2) and m.group(3) is None and not m.group(4):
            return True if value < 0 or value > int(m.group(2)) else False
        elif m.group(1) is None and m.group(2) and m.group(3) == ":" and not m.group(4):
            return True if value < int(m.group(2)) else False
        elif m.group(1) == "~" and not m.group(2) and m.group(3) == ":" and m.group(4):
            return True if value > int(m.group(4)) else False
        elif m.group(1) is None and m.group(2) and m.group(3) == ":" and m.group(4):
            return True if value < int(m.group(2)) or value > int(m.group(4)) else False
        elif m.group(1) == "@" and m.group(2) and m.group(3) == ":" and m.group(4):
            return True if value >= int(m.group(2)) and value <= int(m.group(4)) else False


def exit_by_threshold(threshold, to_print):
    if threshold is not None:
        if type(threshold) is str and threshold:
            print("UNKNOWN - %s" % threshold)
            sys.exit(3)
        elif type(threshold) is bool and threshold:
            print_line(to_print)
            if to_print == "CRITICAL":
                sys.exit(2)
            elif to_print == "WARNING":
                sys.exit(1)


def print_line(status):
    print("%s - %s: %dms | '%s'=%dms;%s;%s;0;" % (status, args.host, result, args.host, result, args.warn, args.crit))


if __name__ == '__main__':
    args = handle_args()
    TRIES += args.retries
    result = None
    if type(args.host) is list:
        args.host = args.host[0]

    if args.tool == "ping":
        result = ping(args.host)
    else:
        print("UNKNOWN - This tool is not supported: " + args.tool)
        sys.exit(3)
    if result is None:
        print("UNKNOWN - An error occurred, maybe the host is not 'pingable'")
        sys.exit(3)
    args.crit = "" if args.crit is None else args.crit
    args.warn = "" if args.warn is None else args.warn
    exit_by_threshold(handle_threshold(result, args.crit), "CRITICAL")
    exit_by_threshold(handle_threshold(result, args.warn), "WARNING")
    print_line("OK")
