#import modules
from base import *
from ui.ui_print import *
import releases

name = "1337x"
session = requests.Session()

def setup(cls, new=False):
    from scraper.services import setup
    setup(cls,new)

def scrape(query, altquery):
    from scraper.services import active
    scraped_releases = []
    if '1337x' in active:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        url = 'https://1337x.to/search/' + str(query) + '/1/'
        try:
            response = session.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            torrentList = soup.select('a[href*="/torrent/"]')
            sizeList = soup.select('td.coll-4')
            seederList = soup.select('td.coll-2')
            if torrentList:
                for count, torrent in enumerate(torrentList):
                    title = torrent.getText().strip()
                    title = title.replace(" ", '.')
                    title = regex.sub(r'\.+', ".", title)
                    if regex.match(r'(' + altquery.replace('.', '\.').replace("\.*", ".*") + ')', title,
                                    regex.I):
                        link = torrent['href']
                        response = session.get('https://1337x.to' + link, headers=headers)
                        soup = BeautifulSoup(response.content, 'html.parser')
                        download = soup.select('a[href^="magnet"]')[0]['href']
                        size = sizeList[count].contents[0]
                        seeders = seederList[count].contents[0]
                        if regex.search(r'([0-9]*?\.[0-9])(?= MB)', size, regex.I):
                            size = regex.search(r'([0-9]*?\.[0-9])(?= MB)', size, regex.I).group()
                            size = float(float(size) / 1000)
                        elif regex.search(r'([0-9]*?\.[0-9])(?= GB)', size, regex.I):
                            size = regex.search(r'([0-9]*?\.[0-9])(?= GB)', size, regex.I).group()
                            size = float(size)
                        else:
                            size = float(size)
                        scraped_releases += [
                            releases.release('[1337x]', 'torrent', title, [], size, [download], seeders=int(seeders))]
        except:
            response = None
            ui_print('1337x error: exception')
    return scraped_releases