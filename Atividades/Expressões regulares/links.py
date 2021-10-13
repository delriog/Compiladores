import re

links = []
arquivo = open('html.txt', 'r')

links = re.findall(r'(?<=href=["\'])https?://.+?(?=["\'])', arquivo.read())

for url in links:
    print(url)


