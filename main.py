#!/usr/bin/env python3
from imaplib import IMAP4_SSL, IMAP4
import pprint
import re
from dotenv import load_dotenv
import os

pp = pprint.PrettyPrinter(indent=4)


def list_mailboxes(M):
    list_response_pattern = re.compile(
        r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')

    def parse_list_response(line):
        flags, delimiter, mailbox_name = list_response_pattern.match(
            line.decode('utf-8')).groups()
        mailbox_name = mailbox_name.strip('"')
        return (flags, delimiter, mailbox_name)

    typ, mailbox_list = M.list()

    print('Listing available mailboxes:')
    for line in mailbox_list:
        flags, delimiter, mailbox_name = parse_list_response(line)
        print(
            f'Mailbox: "{mailbox_name}", Flags: "{flags}", Delimiter: "{delimiter}"')
    print()


def main():
    load_dotenv()

    # surround with doublequotes to allow special characters and spaces in mailbox name
    mailbox = '"' + os.environ['MAILBOX'] + '"'

    with IMAP4_SSL(os.environ['IMAP_SERVER']) as M:
        M.login(os.environ['USERNAME'], os.environ['PASSWORD'])

        list_mailboxes(M)

        try:
            typ, data = M.select(mailbox)

            if typ == 'OK':
                mailbox_message_count = data[0].decode('utf-8')
                print(
                    f'Mailbox select response: {typ}, {mailbox_message_count} messages reported')
            else:
                print(f'Mailbox select failed: {typ}')

            if typ == 'OK':
                messages_found_count = 0
                typ, data = M.search(None, 'FROM', 'service@paypal.de')
                for num in data[0].split():
                    # typ, data = M.fetch(num, '(RFC822)')
                    # print('Message %s\n%s\n' % (num, data[0][1]))
                    messages_found_count += 1
                    message_no = num.decode('utf-8')
                    print(
                        f'Message {message_no}, found {messages_found_count} messages so far')
        except IMAP4.error as e:
            print('IMAP command failed:', e)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Aborted')
