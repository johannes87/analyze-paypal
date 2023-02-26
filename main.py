#!/usr/bin/env python3
from imaplib import IMAP4_SSL, IMAP4
import email
import email.policy
import re
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup


paypal_payment_patterns = [
    re.compile(
        r'.*Sie haben eine Zahlung über (?P<money_amount>.+?) an (?P<money_recipient>.+?) gesendet.*'),
    re.compile(
        r'Bestätigung Ihrer Spende über (?P<money_amount>.+?) an (?P<money_recipient>.+?) mit PayPal'),
    re.compile(
        r'eine Zahlung über (?P<money_amount>.+?) an (?P<money_recipient>.+?) gesendet.'),
    re.compile(
        r'Sie haben eine Handyzahlung über (?P<money_amount>.+?) EUR an (?P<money_recipient>.+?) gesendet'),
    re.compile(
        r'Diese E-Mail bestätigt Ihre Zahlung an (?P<money_recipient>.+?) €(?P<money_amount>.+?) über PayPal'),
    re.compile(
        r'Sie haben eine Zahlung über (?P<money_amount>.+?) an (?P<money_recipient>.+?) autorisiert'),
    re.compile(
        r'Sie haben (?P<money_amount>.+?) an (?P<money_recipient>.+?) gesendet'),
    re.compile(
        r'Sie haben (?P<money_amount>.+?) an (?P<money_recipient>.+?) gespendet'),
    re.compile(
        r'Sie haben eine Zahlung über (?P<money_amount>.+?) an (?P<money_recipient>.+?)\s+genehmigt'),
    re.compile(
        r'Sie haben (?P<money_amount>.+?) gespendet an (?P<money_recipient>.+?)\s+'),
    re.compile(
        r'Sie haben eine Bestellung über (?P<money_amount>.+?) an (?P<money_recipient>.+?) übermittelt'),
    re.compile(
        r'Diese E-Mail bestätigt, dass Sie (?P<money_amount>.+?) an (?P<money_recipient>.+?) mit PayPal bezahlt haben')
]


def list_mailboxes(M):
    list_response_pattern = re.compile(
        r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')

    def parse_list_response(line):
        flags, delimiter, mailbox_name = list_response_pattern.match(
            line.decode('utf-8')).groups()
        mailbox_name = mailbox_name.strip('"')
        return (flags, delimiter, mailbox_name)

    try:
        typ, mailbox_list = M.list()
        if typ == 'OK':
            print('Listing available mailboxes:')
            for line in mailbox_list:
                _, _, mailbox_name = parse_list_response(line)
                print(
                    f'• Mailbox: "{mailbox_name}"')
            print()
        else:
            print(f'Could not list mailboxes: {typ}')
    except IMAP4.error as e:
        print(f'Could not list mailboxes: {e}')


def select_mailbox(M, mailbox) -> bool:
    result = False
    try:
        typ, data = M.select(mailbox)
        if typ == 'OK':
            mailbox_message_count = data[0].decode('utf-8')
            print(
                f'Mailbox select response: {typ}, {mailbox_message_count} messages reported')
            result = True
        else:
            print(f'Could not select mailbox: {typ}')
    except IMAP4.error as e:
        print(f'Could not select mailbox: {e}')
    return result


def fetch_paypal_mails(M, paypal_from, mail_handler):
    messages_processed_count = 0

    try:
        typ, data = M.search(None, 'FROM', paypal_from)
        matching_messages = data[0].split()
        matching_messages_count = len(matching_messages)

        print(
            f'\nFound {matching_messages_count} messages with sender "{paypal_from}"\n')

        for num in matching_messages:
            messages_processed_count += 1
            message_no = num.decode('utf-8')
            try:
                typ, data = M.fetch(num, '(RFC822)')
                if typ == 'OK':
                    mail = email.message_from_bytes(
                        data[0][1], policy=email.policy.default)
                    mail_handler(mail)
                    print(
                        f'IMAP message {message_no}, processed {messages_processed_count} messages so far (of {matching_messages_count})')
                else:
                    print(
                        f'Could not fetch email, IMAP message {message_no}: {typ}')
            except IMAP4.error as e:
                print(f'Could not fetch email, IMAP message {message_no}: {e}')
    except IMAP4.error as e:
        print(f'Could not search for emails from "{paypal_from}": {e}')


def process_paypal_mail(mail):
    print('Subject:', mail['subject'])
    print('Date:', mail['date'])
    print()

    mail_body = mail.get_body(preferencelist=('html', 'plain'))

    if mail_body:
        mail_content = BeautifulSoup(
            mail_body.get_content(), "html5lib").get_text()

        found_payment = False

        for payment_pattern in paypal_payment_patterns:
            payment_pattern_match = payment_pattern.search(mail_content)
            if payment_pattern_match:
                money_amount, money_recipient = payment_pattern_match.groups()
                print((money_amount, money_recipient))
                print()
                found_payment = True
                break

        if not found_payment:
            print('No payment information found in the following email:')
            print(mail_content)
    else:
        print('No HTML or plaintext content found in the following email:')
        print(mail)


def main():
    load_dotenv()

    with IMAP4_SSL(os.environ['IMAP_SERVER']) as M:
        M.login(os.environ['USERNAME'], os.environ['PASSWORD'])
        list_mailboxes(M)

        # surround with doublequotes to allow spaces in mailbox name
        mailbox = '"' + os.environ['MAILBOX'] + '"'
        if select_mailbox(M, mailbox):
            fetch_paypal_mails(
                M, os.environ['PAYPAL_FROM'], process_paypal_mail)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Aborted')
