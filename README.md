# Ugra Gatekeeper Bot

1. Removes any join and leave messages.
2. Removes any channel-originated messages.
3. Adds captcha for joining users.
4. Logs all join actions.

## Installation

* Nix: use `ugragatekeeper` package or `ugragatekeeper` NixOS module from the [flake](https://nixos.wiki/wiki/Flakes)
* Other systems: use [Poetry](https://python-poetry.org/): `poetry install`
* TODO: publish to PyPI/etc

## Usage

```
ugragatekeeper -c CONFIG (-t TCP | -u UNIX) -d DOMAIN
```

* `-c CONFIG` — path to configuration file
* `-t TCP` — host and port to listen on (ex. `127.0.0.1:5050`), or just a port (ex. `5050`), implying listening on all hostnames
* `-u UNIX` — path to UNIX-socket to listen on (ex. `/tmp/gate.sock`)
* `-d DOMAIN` — domain name which will be sent to Telegram

Notes:
1. You need a reverse proxy to support HTTPS. Telegram does not allow HTTP webhooks.
2. You can provide only one of `-t`, `-u` options.

## Configuration

Configuration file is an YAML file. Example is provided in `config-example.yaml`.

### `bot`

Configuration of Telegram bot.

* `bot.token` — Telegram bot token, str, required.
* `bot.chat_id` — Chat ID to manage, int, required.

Bot is single-chat and won't work in others, even if added as an admin.

### `modules`

Configuration of modules. Now there is 5 modules. To enable module, add its key without a parameters. Example:

```yaml
modules:
    some_module: {}
```

You may also specify some options, if supported:

```yaml
modules:
    some_module:
        some_option: value
```

#### `modules.logging`

Logs all actions to Telegram.

* `modules.logging.chat_id` — Chat ID to log into, int, required.

If it's a channel or group (negative value), bot should be added to chat. If it's a user (positive value), you should start conversation with a bot.

If module is disabled, bot will log to stderr.

#### `modules.remove_joins`

Removes messages `X was accepted into group`, `X joined the group`, etc.

No options.

#### `modules.remove_leaves`

Removes messages `X left the group`, `X removed Y`, etc.

#### `modules.remove_channel_messages`

Removes all anonymous messages.

This is not applied to anonymous admins of the current group, messages from the linked channel (both forwarded posts and anonymous) and allowed channels.

* `modules.remove_channel_messages.exceptions` — IDs of allowed channels for anonymous posting, list[int], optional, default is empty

#### `modules.process_join_requests`

Enables processing of chat join requests. You should enable “Request Admin Approval” in private chats or “Who can send messages? → Only members, Approve new members” in public chats.

If public chat is linked to a channel, you should protect comments as well.

When someone tries to join the chat, bot will send question to them. If they answer correctly, they are approved. The number of tries is unlimited.

* `modules.process_join_requests.question` — Question text, str, required
* `modules.process_join_requests.answer` — Correct answer, str, required
* `modules.process_join_requests.correct_feedback` — Feedback for correct answer, str, required
* `modules.process_join_requests.incorrect_feedback` — Feedback for wrong answer, str, required
* `modules.process_join_requests.approve_failed` — Feedback when approve failed, str, required

Notes:
1. Correct answer is checked the following way: `config.answer in message.text.lower()`
2. Approve may fail, if user deleted the group or was approved by admin manually, or send answer after the first approval.

## NixOS deployment

The project provides module `ugragatekeeper` with three options:

* `config` — configuration with the same keys as above
* `privateConfigFile` — path to YAML file with “secret” keys (like `bot.token`), will be merged into config using `yaml-merge`
* `domain` — domain name for `-d`

The module uses nginx as a reverse proxy.

## TODO

1. Add Telegram Premium users right away.
2. Add users that were approved once right away.
3. Add other metrics.
