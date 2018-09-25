import os
import socket
import time
import sys

def debug(message, message_level=1):
    level = int(os.environ.get('DEBUG', 1))

    if level >= message_level:
        timestamp = time.strftime('%H:%M:%S', time.gmtime(time.time()))
        node = socket.gethostname()
        print(f'{timestamp} {node} DEBUG({message_level}): {message}', file=sys.stderr)
