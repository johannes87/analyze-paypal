
import email
from imaplib import IMAP4_SSL, IMAP4
import pickle
from analyze_paypal import configuration
from analyze_paypal.configuration import Configuration
from analyze_paypal.exceptions import FetchMailsException


class MailsContainer:
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration
        self.mails = []

    def fetch_mails(self):
        with IMAP4_SSL(self.configuration.imap_server) as imap_handle:
            imap_handle.login(self.configuration.username,
                              self.configuration.password)

            # surround with doublequotes to allow spaces in mailbox name
            imap_result, _ = imap_handle.select(
                f"\"{self.configuration.mailbox}\"")

            if imap_result != 'OK':
                raise FetchMailsException('Could not select mailbox')

            imap_result, imap_data = imap_handle.search(
                None, 'FROM', self.configuration.paypal_from)
            matching_message_nums = imap_data[0].split()

            print(f"Now fetching {len(matching_message_nums)} messages")
            fetched_count = 0
            for message_num in matching_message_nums:
                imap_result, imap_data = imap_handle.fetch(
                    message_num, '(RFC822)')
                if imap_result != 'OK':
                    raise FetchMailsException(
                        f"Could not fetch message number {message_num}")
                message = email.message_from_bytes(
                    imap_data[0][1], policy=email.policy.default)
                self.mails.append(message)
                fetched_count += 1
                print(f"Fetched {fetched_count} messages")

    def export_mails(self, file_path):
        with open(file_path, "wb") as out_file:
            pickle.dump(self.mails, out_file)

    def import_mails(self, file_path):
        with open(file_path, "rb") as in_file:
            self.mails = pickle.load(in_file)
