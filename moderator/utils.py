import errno
import hashlib
import logging
import os
import socket
import stat

from aiogram.types import Message, Chat, User, ChatJoinRequest

logger = logging.getLogger(__name__)


# See: https://github.com/aio-libs/aiohttp/issues/4155
def prepare_socket(path: str) -> socket.socket:
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


def get_webhook_path(path: str) -> str:
    return f"/{hashlib.sha256(path.encode()).hexdigest()}"


def format_user(user: User) -> str:
    if user.username:
        return f"[{user.id}] @{user.username}"
    else:
        return f"""[{user.id}] <a href="tg://user?id={user.id}">{user.first_name} {user.last_name or ""}</a>"""


def format_channel(channel: Chat) -> str:
    return f"[{channel.id}] {channel.title} (@{channel.username})"


def format_message(message: Message, reason: str) -> str:
    match reason:
        case "leave":
            return f"User left from chat: {format_user(message.left_chat_member)}"
        case "join":
            return f"User joined the chat: {', '.join(map(format_user, message.new_chat_members))}"
        case "channel":
            return f"Someone posted anonymous message: {message.md_text[:30]} on behalf of {format_channel(message.sender_chat)}"


def format_join_request(request: ChatJoinRequest) -> str:
    return f"User requested to join: {format_user(request.from_user)}"


__all__ = ["prepare_socket", "get_webhook_path", "format_message", "format_join_request"]
