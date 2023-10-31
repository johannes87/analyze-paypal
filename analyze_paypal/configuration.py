import argparse
from dataclasses import dataclass


@dataclass
class Configuration:
    username: str
    password: str
    imap_server: str
    mailbox: str
    paypal_from: str
    pattern: str
    fetch_file_path: str
    analyze_file_path: str

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--username', required=False,
                            help='the IMAP username')
        parser.add_argument('--password', required=False,
                            help='the IMAP password')
        parser.add_argument('--server', required=False, help='the IMAP server')
        parser.add_argument('--mailbox', required=False,
                            help='the IMAP mailbox which is searched for mails')
        parser.add_argument('--paypal-from', dest='paypal_from', required=False,
                            help='the sender address of the paypal mails. mails inside the --mailbox are searched for this sender address')
        parser.add_argument('--fetch', required=False, dest='output_file_path',
                            help='the path to the file where fetched emails should be stored')
        parser.add_argument('--analyze', required=False, dest='input_file_path',
                            help='the path to the file where the previously fetched emails were stored, and which should now be analyzed')
        parser.add_argument('--pattern', required=False,
                            help='the pattern to search for in the mails. needs to have one group, which is the money amount')
        args = parser.parse_args()

        self.__assert_valid_arguments(parser, args)

        self.username = args.username
        self.password = args.password
        self.imap_server = args.server
        self.mailbox = args.mailbox
        self.paypal_from = args.paypal_from
        self.fetch_file_path = args.output_file_path
        self.analyze_file_path = args.input_file_path
        self.pattern = args.pattern

    def __assert_valid_arguments(self, parser, args):
        if not any(vars(args).values()):
            parser.print_help()
        if args.output_file_path and args.input_file_path:
            print('Either specify --fetch or --analyze, but not both. See --help.')
            parser.exit()
        if args.output_file_path and not (args.username and args.password and args.server and args.mailbox and args.paypal_from):
            print('When using --fetch, you need to also specify: username, password, server, mailbox, and paypal-from. See --help.')
            parser.exit()
        if args.input_file_path and not args.pattern:
            print(
                'When using --analyzed, you also need to specify a pattern. See --help.')
            parser.exit()
