from bs4 import BeautifulSoup


def html_to_text(html):
    soup = BeautifulSoup(html)
    return soup.get_text()
