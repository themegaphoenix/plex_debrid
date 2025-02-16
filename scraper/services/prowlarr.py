#import modules
from base import *
from ui.ui_print import *
import releases

base_url = "http://127.0.0.1:9696"
api_key = ""
name = "prowlarr"
session = requests.Session()

def setup(cls, new=False):
    from scraper.services import setup
    setup(cls,new)

def scrape(query, altquery):
    from scraper.services import active
    scraped_releases = []
    if 'prowlarr' in active:
        url = base_url + '/api/v1/search?query=' + query + '&type=search&limit=1000&offset=0'
        headers = {'X-Api-Key': api_key}
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            for result in response[:]:
                result.title = result.title.replace(' ', '.')
                if regex.match(r'(' + altquery.replace('.', '\.').replace("\.*", ".*") + ')', result.title,
                                regex.I) and result.protocol == 'torrent':
                    if hasattr(result, 'magnetUrl'):
                        if not result.magnetUrl == None:
                            if not result.indexer == None and not result.size == None:
                                scraped_releases += [
                                    releases.release('[prowlarr: ' + str(result.indexer) + ']', 'torrent', result.title,
                                                [], float(result.size) / 1000000000, [result.magnetUrl],
                                                seeders=result.seeders)]
                            elif not result.indexer == None:
                                scraped_releases += [
                                    releases.release('[prowlarr: ' + str(result.indexer) + ']', 'torrent', result.title,
                                                [], 1, [result.magnetUrl], seeders=result.seeders)]
                            elif not result.size == None:
                                scraped_releases += [
                                    releases.release('[prowlarr: unnamed]', 'torrent', result.title, [],
                                                float(result.size) / 1000000000, [result.magnetUrl],
                                                seeders=result.seeders)]
                            response.remove(result)
                else:
                    response.remove(result)
            # Multiprocess resolving of result.Link for remaining releases
            results = [None] * len(response)
            threads = []
            # start thread for each remaining release
            for index, result in enumerate(response):
                t = Thread(target=multi_init, args=(resolve, result, results, index))
                threads.append(t)
                t.start()
            # wait for the threads to complete
            for t in threads:
                t.join()
            for result in results:
                if not result == []:
                    scraped_releases += result
    return scraped_releases

def resolve(result):
    scraped_releases = []
    try:
        link = session.get(result.downloadUrl, allow_redirects=False, timeout=2)
        if 'Location' in link.headers:
            if regex.search(r'(?<=btih:).*?(?=&)', str(link.headers['Location']), regex.I):
                if not result.indexer == None and not result.size == None:
                    scraped_releases += [
                        releases.release('[prowlarr: ' + str(result.indexer) + ']', 'torrent', result.title, [],
                                    float(result.size) / 1000000000, [link.headers['Location']],
                                    seeders=result.seeders)]
                elif not result.indexer == None:
                    scraped_releases += [
                        releases.release('[prowlarr: ' + str(result.indexer) + ']', 'torrent', result.title, [], 1,
                                    [link.headers['Location']], seeders=result.seeders)]
                elif not result.size == None:
                    scraped_releases += [releases.release('[prowlarr: unnamed]', 'torrent', result.title, [],
                                                    float(result.size) / 1000000000, [link.headers['Location']],
                                                    seeders=result.seeders)]
            return scraped_releases
        elif link.headers['Content-Type'] == "application/x-bittorrent":
            magnet = releases.torrent2magnet(link.content)
            if not result.indexer == None and not result.size == None:
                scraped_releases += [
                    releases.release('[prowlarr: ' + str(result.indexer) + ']', 'torrent', result.title, [],
                                float(result.size) / 1000000000, [magnet], seeders=result.seeders)]
            elif not result.indexer == None:
                scraped_releases += [
                    releases.release('[prowlarr: ' + str(result.indexer) + ']', 'torrent', result.title, [], 1,
                                [magnet], seeders=result.seeders)]
            elif not result.size == None:
                scraped_releases += [releases.release('[prowlarr: unnamed]', 'torrent', result.title, [],
                                                float(result.size) / 1000000000, [magnet],
                                                seeders=result.seeders)]
            return scraped_releases
    except:
        return scraped_releases

    
# Multiprocessing watchlist method
def multi_init(cls, obj, result, index):
    result[index] = cls(obj)