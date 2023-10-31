#!/usr/bin/env python3
from analyze_paypal.analyze_mails import AnalyzeMails
from analyze_paypal.configuration import Configuration
from analyze_paypal.mails_container import MailsContainer


def main():
    configuration = Configuration()
    mails_container = MailsContainer(configuration)
    if configuration.fetch_file_path:
        mails_container.fetch_mails()
        mails_container.export_mails(configuration.fetch_file_path)
    elif configuration.analyze_file_path:
        mails_container.import_mails(configuration.analyze_file_path)
        analyze_mails = AnalyzeMails(mails_container)
        analyze_mails.analyze(configuration.pattern)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Aborted')
