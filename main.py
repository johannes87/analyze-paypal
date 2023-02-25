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
        _, _, mailbox_name = parse_list_response(line)
        print(
            f'• Mailbox: "{mailbox_name}"')
    print()


def main():
    load_dotenv()

    # surround with doublequotes to allow spaces in mailbox name
    mailbox = '"' + os.environ['MAILBOX'] + '"'
    paypal_from = os.environ['PAYPAL_FROM']

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
                messages_processed_count = 0
                typ, data = M.search(None, 'FROM', paypal_from)

                matching_messages = data[0].split()
                matching_messages_count = len(matching_messages)

                print(
                    f'\nFound {matching_messages_count} messages with sender "{paypal_from}"\n')

                for num in matching_messages:
                    messages_processed_count += 1
                    message_no = num.decode('utf-8')

                    print(
                        f'Message {message_no}, processed {messages_processed_count} messages so far (of {matching_messages_count})')

                    typ, data = M.fetch(num, '(RFC822)')
                    # print('Message %s\n%s\n' % (num, data[0][1]))
                    # pp.pprint(data)
        except IMAP4.error as e:
            print('IMAP command failed:', e)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Aborted')
