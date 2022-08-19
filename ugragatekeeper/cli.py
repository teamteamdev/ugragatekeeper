import argparse
import yaml

from ugragatekeeper import app, utils


def construct_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Moderation bot for Telegram")
    parser.add_argument(
        "-c", "--config", required=True,
        help="path to YAML file"
    )
    listen_group = parser.add_mutually_exclusive_group(required=True)
    listen_group.add_argument("-t", "--tcp", help="host and port separated by :")
    listen_group.add_argument("-u", "--unix", help="path to UNIX socket")
    parser.add_argument("-d", "--domain", required=True, help="public domain, with scheme and port")

    return parser


def main():
    parser = construct_parser()
    args = parser.parse_args()

    try:
        with open(args.config, "r") as config_file:
            config = yaml.safe_load(config_file.read())
    except IOError:
        raise RuntimeError("Can not read config file")
    except yaml.error.YAMLError:
        raise RuntimeError("Can not parse config file")

    if args.tcp:
        *host, port = args.tcp.rsplit(":", 1)
        host = host[0] if len(host) > 0 else None
        network_options = {
            "host": host,
            "port": port
        }
    elif args.unix:
        network_options = {
            "sock": utils.prepare_socket(args.unix)
        }
    else:
        raise RuntimeError("Neither args.tcp not args.unix provided")

    app.run(domain=args.domain, config=config, network_options=network_options)
