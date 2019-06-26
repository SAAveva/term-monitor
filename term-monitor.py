#!/usr/bin/env python3

import re
import os
import sys
import shlex
import select
from subprocess import Popen, PIPE
import ast
from time import sleep

usage = '{} <pid>'.format(sys.argv[0])
command = 'strace -f -s999 -e trace=write -p {}'

def echo(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()

if __name__ == '__main__':
    try:
        pid = sys.argv[1]
    except IndexError:
        echo(usage, file=sys.stderr)
        exit(-1)

    if os.geteuid() != 0:
        print("{} must be run as root".format(sys.argv[0]), file=sys.stderr)
        exit(-2)

    process = Popen(shlex.split(command.format(pid)), stderr=PIPE, stdout=PIPE)
    pattern = re.compile('write\(\d, \"(.+?)\"')

    try:
        while True:
            r, w, x = select.select([process.stdout, process.stderr], [], [])
            fileno = r[0].fileno()
            out = os.read(fileno, 1024)

            if not out:
                continue

            out = str(out)
            match=  pattern.search(out)
            if match:
                match = match.group(1)
                escaped = match.encode().decode('unicode-escape')
                escaped = escaped.rstrip('\\')
                escaped = escaped.encode().decode('unicode-escape')
                echo(escaped, end='')
    except KeyboardInterrupt:
        echo('\nExisting..\n')
        exit(0)
