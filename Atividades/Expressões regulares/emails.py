import re

emails = []
arquivo = open('e-mails.txt', 'r')

emails = re.findall(r'(?<=<)(.*?)(?=>)',arquivo.read())

for email in emails:
    print(email)
