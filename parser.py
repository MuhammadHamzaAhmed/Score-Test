from bs4 import BeautifulSoup


class Parser:
    def get_tags(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        tags = soup.find_all('p')
        return [tag.text for tag in tags]
