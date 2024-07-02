import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from bs4.element import Comment
from hash_table import HashQP
from MinHeap import MinHeap

class ResultEntry:
    def __init__(self, site, score):
        self._site = site
        self._score = score

    @property
    def site(self):
        return self._site

    @property
    def score(self):
        return self._score

    def __lt__(self, other):
        if isinstance(other, ResultEntry):
            return self._score < other._score
        return self._score < other

    def __gt__(self, other):
        if isinstance(other, ResultEntry):
            return self._score > other._score
        return self._score > other

    def __eq__(self, other):
        if isinstance(other, ResultEntry):
            return self._score == other._score
        return self._score == other

class KeywordEntry:
    def __init__(self, word: str, url: str = None, location: int = None):
        self._word = word.upper()
        if url:
            self._sites = {url: [location]}
        else:
            self._sites = {}

    def add(self, url: str, location: int) -> None:
        if url in self._sites:
            self._sites[url].append(location)
        else:
            self._sites[url] = [location]

    def get_locations(self, url: str) -> list:
        try:
            return self._sites[url]
        except IndexError:
            return []

    @property
    def sites(self) -> list:
        return [key for key in self._sites]

    def __lt__(self, other):
        if isinstance(other, KeywordEntry):
            return self._word < other._word
        else:
            return self._word < other.upper()

    def __gt__(self, other):
        if isinstance(other, KeywordEntry):
            return self._word > other._word
        else:
            return self._word > other.upper()

    def __eq__(self, other):
        if isinstance(other, KeywordEntry):
            return self._word == other._word
        else:
            return self._word == other.upper()

    def __hash__(self):
        return hash(self._word)

def link_fisher(url, depth=0, reg_ex=""):
    res = _link_fisher(url, depth, reg_ex)
    res.append(url)
    return list(set(res))

def _link_fisher(url, depth, reg_ex):
    link_list = []
    if depth == 0:
        return link_list
    headers = {
        'User-Agent': ''
    }
    try:
        page = requests.get(url, headers=headers)
    except:
        print("Cannot retrieve", url)
        return link_list
    data = page.text
    soup = BeautifulSoup(data, features="html.parser")
    for link in soup.find_all('a', attrs={'href': re.compile(reg_ex)}):
        link_list.append(urljoin(url, link.get('href')))
    for i in range(len(link_list)):
        link_list.extend(_link_fisher(link_list[i], depth - 1, reg_ex))
    return link_list

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def words_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.find_all(string=True)
    visible_texts = filter(tag_visible, texts)
    text_string = " ".join(t for t in visible_texts)
    words = re.findall(r'\w+', text_string)
    return words

def text_harvester(url):
    headers = {
        'User-Agent': ''}
    try:
        page = requests.get(url, headers=headers)
    except:
        return []
    res = words_from_html(page.content)
    return res

class WebStore:
    def __init__(self, ds):
        self._store = ds()
        self._search_result = MinHeap()

    def crawl(self, url: str, depth=0, reg_ex=''):
        links = link_fisher(url, depth, reg_ex)
        for link in links:
            text = text_harvester(link)
            for location, word in enumerate(text):
                if not word.isalpha() or len(word) < 4:
                    continue
                k_e = KeywordEntry(word, link, location)
                if k_e in self._store:
                    existing_k_e = self._store.find(k_e)
                    existing_k_e.add(link, location)
                else:
                    self._store.insert(k_e)
    def search(self, keyword: str):
        try:
            k_e = self._store.find(KeywordEntry(keyword))
            if k_e:
                return k_e.sites
            else:
                return []
        except HashQP.NotFoundError:
            return []
    def search_pair(self, term_one: str, term_two: str) -> bool:
        self._search_result = MinHeap()
        try:
            keyword_one = self._store.find(KeywordEntry(term_one))
            keyword_two = self._store.find(KeywordEntry(term_two))
        except HashQP.NotFoundError:
            return False
        pages_one = set(keyword_one.sites)
        pages_two = set(keyword_two.sites)
        common_pages = pages_one & pages_two

        for page in common_pages:
            loc_one = keyword_one.get_locations(page)[0] + 1
            loc_two = keyword_two.get_locations(page)[0] + 1
            freq_one = len(keyword_one.get_locations(page))
            freq_two = len(keyword_two.get_locations(page))
            proximity_to_top = loc_one * loc_two
            frequency = (1 / freq_one) * (1 / freq_two)
            proximity_to_each_other = min(
                abs(pos1 - pos2) for pos1 in keyword_one.get_locations(page) for pos2 in keyword_two.get_locations(page)
            )

            if term_one == term_two:
                proximity_to_each_other = 1
            score = proximity_to_top * frequency * proximity_to_each_other
            result_entry = ResultEntry(page, score)
            self._search_result.insert(result_entry)
        return True

    def get_result(self) -> ResultEntry:
        try:
            return self._search_result.remove()
        except MinHeap.EmptyHeapError:
            raise IndexError("Results not available")



if __name__ == "__main__":
    store = WebStore(HashQP)
    store.crawl("http://compsci.mrreed.com", 2)

    while True:
        term_one = input("Enter first term: ")
        term_two = input("Enter second term: ")
        store.search_pair(term_one, term_two)
        while True:
            try:
                result = store.get_result()
                print(result.site, round(result.score, 1))
            except IndexError:
                break
        print()


"""
/Users/buyantogtokh/PycharmProjects/june/.venv/bin/python /Users/buyantogtokh/PycharmProjects/june/minisearchengine.py 
Enter first term: persistent
Enter second term: defect

Enter first term: placement
Enter second term: defect
http://compsci.mrreed.com 5.6
http://compsci.mrreed.com/index.html 5.6

Enter first term: waters
Enter second term: waters
http://compsci.mrreed.com/4820.html 100.0
http://compsci.mrreed.com/2649.html 7744.0

Enter first term: scissors
Enter second term: scissors
http://compsci.mrreed.com/2649.html 4.0
http://compsci.mrreed.com/7918.html 100.0
http://compsci.mrreed.com/5738.html 400.0
http://compsci.mrreed.com/8167.html 484.0
http://compsci.mrreed.com/4542.html 6889.0

Enter first term: scissors
Enter second term: floor
http://compsci.mrreed.com/2649.html 1920.0
http://compsci.mrreed.com/4542.html 114540.0

Enter first term: fkiir
Enter second term: fkiir

Enter first term: floor
Enter second term: scissors
http://compsci.mrreed.com/2649.html 1920.0
http://compsci.mrreed.com/4542.html 114540.0

Enter first term: gas
Enter second term: practices

Enter first term: ceilings
Enter second term: noon
http://compsci.mrreed.com/4542.html 22440.0

Enter first term: seals
Enter second term: seals
http://compsci.mrreed.com/3845.html 100.0
http://compsci.mrreed.com/4542.html 1024.0
"""