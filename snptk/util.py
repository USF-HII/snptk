import os
import socket
import time
import sys

def debug(message, level=1):
    debug_level = int(os.environ.get('DEBUG', 0))

    if debug_level >= level:
        timestamp = time.strftime('%F %H:%M:%S', time.gmtime(time.time()))
        node = socket.gethostname()
        print(f'{timestamp} {node} DEBUG({level}): {message}', file=sys.stderr)
