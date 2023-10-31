import re

from bs4 import BeautifulSoup
from analyze_paypal.mails_container import MailsContainer


class AnalyzeMails:
    def __init__(self, mails_container: MailsContainer) -> None:
        self.mails_container = mails_container

    def analyze(self, pattern):
        self.mails_container.mails.reverse()
        money_sum = 0
        for mail in self.mails_container.mails:
            mail_body = mail.get_body(preferencelist=('html', 'plain'))
            mail_content = BeautifulSoup(
                mail_body.get_content(), "html5lib").get_text()

            match = re.search(re.compile(pattern), mail_content)
            if match:
                money_amount_raw = match.group(1)
                money_amount = float(money_amount_raw.replace(',', '.'))
                print(f"Amount: {money_amount} Date: {mail['date']}")
                money_sum += money_amount
        print(f"Money sum is: {money_sum}")
