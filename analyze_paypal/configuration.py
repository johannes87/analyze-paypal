from dataclasses import dataclass
import os


@dataclass
class Configuration:
    username: str
    password: str
    imap_server: str
    mailbox: str
    paypal_from: str

    def __init__(self):
        self.username = os.environ['USERNAME']
        self.password = os.environ['PASSWORD']
        self.imap_server = os.environ['IMAP_SERVER']
        self.mailbox = os.environ['MAILBOX']
        self.paypal_from = os.environ['PAYPAL_FROM']
