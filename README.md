# Motivation
I wanted to see how much money I spent with ordering takeout food. Each order creates an email. By analyzing the emails I can see how much money I spent, for example, ordering from Wolt.

# Usage

It's a two-step process. First fetching the emails (which are then stored in a file), and later analyzing the emails.

## Fetch the emails
```
./main.py --fetch mails.pickle --username your-email@gmail.com --password your-password --mailbox '[Gmail]/Alle Nachrichten' --paypal-from 'service@paypal.de' --server imap.gmail.com
```

## Analyze the emails
```
./main.py --analyze mails.pickle --pattern '*Sie haben eine Zahlung über €(.*).EUR an Wolt Enterprises Deutschland GmbH autorisiert.*'
```

The `(.*)` part of the regex pattern needs to be the money (and only the money) value.