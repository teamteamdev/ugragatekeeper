import errno
import logging
import os
import sys
import stat
import socket

from aiohttp import web

logger = logging.getLogger(__name__)


async def hello(request):
    return web.Response(text="Hello, world")


async def on_startup(app: web.Application):
    os.chmod(sys.argv[4], 0o777)


# See: https://github.com/aio-libs/aiohttp/issues/4155
def prepare_socket() -> socket.socket:
    path = sys.argv[4]
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    try:
        if stat.S_ISSOCK(os.stat(path).st_mode):
            os.remove(path)
    except FileNotFoundError:
        pass
    except OSError as err:
        logger.error('Unable to check or remove stale UNIX socket '
                    '%r: %r', path, err)

    try:
        sock.bind(path)
    except OSError as exc:
        sock.close()
        if exc.errno == errno.EADDRINUSE:
            msg = f'Address {path!r} is already in use'
            raise OSError(errno.EADDRINUSE, msg) from None
        else:
            raise
    except:
        sock.close()
        raise

    os.chmod(path, 0o777)

    return sock


def main():

    app = web.Application()
    app.add_routes([web.get('/', hello)])
    app.on_startup.append(on_startup)

    web.run_app(app, sock=prepare_socket())
