import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":
    subject = 'Nathan Fillion'

    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'parse',
        'page': subject,
        'format': 'json',
        'prop': 'text',
        'redirects': ''
    }

    response = requests.get(url, params=params)
    data = response.json()

    raw_html = data['parse']['text']['*']
    soup = BeautifulSoup(raw_html, 'html.parser')
    # soup.find_all('p')
    text = ''
    for c in soup.find_all("h2"):
        print(c, "====================")
        print(c.text)
        # for c1 in c.children:
        #     print(c1.text)


    # for p in soup.find_all('h2'):
    #     text += p.text
    #
    # print(text[:58])
    # print('Text length: ', len(text))
    # print(text)
