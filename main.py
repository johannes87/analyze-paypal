#!/usr/bin/env python3
from dotenv import load_dotenv
import sys
from analyze_paypal.analyze_mails import AnalyzeMails
from analyze_paypal.configuration import Configuration
from analyze_paypal.mails_container import MailsContainer


def main():
    load_dotenv()
    configuration = Configuration()
    mails_container = MailsContainer(configuration)
    # mails_container.fetch_mails()
    # mails_container.export_mails("mails.pickle")
    mails_container.import_mails("mails.pickle")
    analyze_mails = AnalyzeMails(mails_container)
    analyze_mails.analyze(
        r'.*Sie haben eine Zahlung über €(.*).EUR an Wolt Enterprises Deutschland GmbH autorisiert.*')
    sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Aborted')
