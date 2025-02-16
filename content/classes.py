from base import *

import releases
import debrid
import scraper
from ui.ui_print import *

class watchlist(Sequence):
    def __init__(self, other):
        self.data = other

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)

    def __eq__(self, other):
        return len(self) == len(other)

    def remove(self, item):
        self.data.remove(item)

    def add(self, item, user):
        self.data.append(item)

class library:
    active = []

    def setup(cls, new=False):
        from settings import settings_list
        settings = []
        for category, allsettings in settings_list:
            for setting in allsettings:
                if setting.cls == cls or setting.name.startswith(cls.name):
                    settings += [setting]
        back = False
        if not new:
            while not back:
                print("0) Back")
                indices = []
                for index, setting in enumerate(settings):
                    print(str(index + 1) + ') ' + setting.name)
                    indices += [str(index + 1)]
                print()
                choice = input("Choose an action: ")
                if choice in indices:
                    settings[int(choice) - 1].input()
                    if not cls.name in library.active:
                        library.active = [cls.name]
                    back = True
                elif choice == '0':
                    back = True
        else:
            print()
            indices = []
            for setting in settings:
                setting.setup()
                if not cls.name in library.active:
                    library.active = [cls.name]

    def __new__(cls):
        activeservices = []
        for servicename in library.active:
            for service in cls.__subclasses__():
                if service.name == servicename:
                    activeservices += [service]
        return activeservices


class media:
    ignore_queue = []
    downloaded_versions = []

    def __init__(self, other):
        self.__dict__.update(other.__dict__)

    def __eq__(self, other) -> bool:
        try:
            if not self.type == other.type:
                return False
            if self.type == 'movie' or self.type == 'show':
                return self.guid == other.guid
            elif self.type == 'season':
                return self.parentGuid == other.parentGuid and self.index == other.index
            elif self.type == 'episode':
                return self.grandparentGuid == other.grandparentGuid and self.parentIndex == other.parentIndex and self.index == other.index
        except:
            return False

    def __repr__(self):
        return str(self.__dict__)

    def query(self):
        if self.type == 'movie':
            title = releases.rename(self.title)
            title = title.replace('.' + str(self.year), '')
            return title + '.' + str(self.year)
        elif self.type == 'show':
            title = releases.rename(self.title)
            title = title.replace('.' + str(self.year), '')
            return title
        elif self.type == 'season':
            title = releases.rename(self.parentTitle)
            title = title.replace('.' + str(self.parentYear), '')
            return title + '.S' + str("{:02d}".format(self.index)) + '.'
        elif self.type == 'episode':
            title = releases.rename(self.grandparentTitle)
            title = title.replace('.' + str(self.grandparentYear), '')
            return title + '.S' + str("{:02d}".format(self.parentIndex)) + 'E' + str(
                "{:02d}".format(self.index)) + '.'

    def deviation(self):
        if self.type == 'movie':
            title = releases.rename(self.title)
            title = title.replace('.' + str(self.year), '')
            return '(' + title + '.)(' + str(self.year) + '|' + str(self.year - 1) + '|' + str(self.year + 1) + ')'
        elif self.type == 'show':
            title = releases.rename(self.title)
            title = title.replace('.' + str(self.year), '')
            return '(' + title + '.)((' + str(
                self.year) + '.)|(complete.)|(seasons?.[0-9]+.[0-9]?[0-9]?.?)|(S[0-9]+.[0-9]?[0-9]?.?)|(S[0-9]+E[0-9]+))'
        elif self.type == 'season':
            title = releases.rename(self.parentTitle)
            title = title.replace('.' + str(self.parentYear), '')
            return '(' + title + '.)(' + str(self.parentYear) + '.)?(season.[0-9]+.)?' + '(S' + str(
                "{:02d}".format(self.index)) + '.)'
        elif self.type == 'episode':
            title = releases.rename(self.grandparentTitle)
            title = title.replace('.' + str(self.grandparentYear), '')
            return '(' + title + '.)(' + str(self.grandparentYear) + '.)?(S' + str(
                "{:02d}".format(self.parentIndex)) + 'E' + str("{:02d}".format(self.index)) + '.)'

    def versions(self):
        versions = []
        for version in releases.sort.versions:
            versions += [releases.sort.version(version[0], version[1], version[2], version[3])]
        for version in versions[:]:
            if self.query() + ' [' + version.name + ']' in media.downloaded_versions:
                versions.remove(version)
        return versions

    def version_missing(self):
        return (len(self.versions()) > 0) and not (len(self.versions()) == len(releases.sort.versions))

    def watch(self):
        import content.services.plex as plex
        import content.services.trakt as trakt
        import content.services.overseerr as overseerr
        if not self in media.ignore_queue:
            self.ignored_count = 1
            media.ignore_queue += [self]
            ui_print('retrying download in 30min for item: ' + self.query() + ' - attempt ' + str(
                self.ignored_count) + '/48')
        else:
            match = next((x for x in media.ignore_queue if self == x), None)
            if match.ignored_count < 48:
                match.ignored_count += 1
                ui_print('retrying download in 30min for item: ' + self.query() + ' - attempt ' + str(
                    match.ignored_count) + '/48')
            else:
                media.ignore_queue.remove(match)
                if library.active == ['Plex Library']:
                    try:
                        ui_print('[plex] ignoring item: ' + self.query())
                        url = 'https://metadata.provider.plex.tv/actions/scrobble?identifier=tv.plex.provider.metadata&key=' + self.ratingKey + '&X-Plex-Token=' + \
                                plex.users[0][1]
                        plex.get(url)
                        if not self in plex.ignored:
                            plex.ignored += [self]
                    except Exception as e:
                        ui_print("plex error: couldnt ignore item: " + str(e), debug=ui_settings.debug)
                elif library.active == ['Trakt Collection']:
                    pass

    def unwatch(self):
        import content.services.plex as plex
        import content.services.trakt as trakt
        import content.services.overseerr as overseerr
        if library.active == ['Plex Library']:
            try:
                url = 'https://metadata.provider.plex.tv/actions/unscrobble?identifier=tv.plex.provider.metadata&key=' + self.ratingKey + '&X-Plex-Token=' + \
                        plex.users[0][1]
                plex.get(url)
                plex.ignored.remove(self)
            except Exception as e:
                ui_print("plex error: couldnt un-ignore item: " + str(e), debug=ui_settings.debug)
        elif library.active == ['Trakt Collection']:
            pass

    def released(self):
        try:
            released = datetime.datetime.today() - datetime.datetime.strptime(self.originallyAvailableAt,
                                                                                '%Y-%m-%d')
            if self.type == 'movie':
                if released.days >= -30 and released.days <= 60:
                    if self.available():
                        return True
                    else:
                        return False
                return released.days > 0
            else:
                if released.days >= 0 and released.days <= 1:
                    if self.available():
                        return True
                    else:
                        return False
                return released.days >= 0
        except Exception as e:
            ui_print("media error: (attr exception): " + str(e), debug=ui_settings.debug)
            return False

    def available(self):
        import content.services.plex as plex
        import content.services.trakt as trakt
        import content.services.overseerr as overseerr
        if (self.watchlist == plex.watchlist and len(trakt.users) > 0) or self.watchlist == trakt.watchlist:
            if self.watchlist == plex.watchlist:
                try:
                    for guid in self.Guid:
                        service, guid = guid.id.split('://')
                        trakt_match = trakt.match(guid, service, self.type)
                        if not trakt_match == None:
                            break
                except Exception as e:
                    ui_print("plex error: (attr exception): " + str(e), debug=ui_settings.debug)
                    return True
            else:
                trakt_match = self
            if not trakt_match == None:
                trakt.current_user = trakt.users[0]
                try:
                    if trakt_match.type == 'show':
                        return datetime.datetime.utcnow() > datetime.datetime.strptime(trakt_match.first_aired,
                                                                                        '%Y-%m-%dT%H:%M:%S.000Z')
                    elif trakt_match.type == 'movie':
                        release_date = None
                        releases, header = trakt.get(
                            'https://api.trakt.tv/movies/' + str(trakt_match.ids.trakt) + '/releases/')
                        for release in releases:
                            if release.release_type == 'digital' or release.release_type == 'physical' or release.release_type == 'tv':
                                if release_date == None:
                                    release_date = release.release_date
                                elif datetime.datetime.strptime(release_date,
                                                                '%Y-%m-%d') > datetime.datetime.strptime(
                                        release.release_date, '%Y-%m-%d'):
                                    release_date = release.release_date
                        # If no release date was found, select the theatrical release date + 2 Month delay
                        if release_date == None:
                            for release in releases:
                                if release_date == None:
                                    release_date = release.release_date
                                elif datetime.datetime.strptime(release_date,
                                                                '%Y-%m-%d') > datetime.datetime.strptime(
                                        release.release_date, '%Y-%m-%d'):
                                    release_date = release.release_date
                            release_date = datetime.datetime.strptime(release_date,
                                                                        '%Y-%m-%d') + datetime.timedelta(days=60)
                            release_date = release_date.strftime("%Y-%m-%d")
                        # Get trakt 'Latest HD/4k Releases' Lists to accept early releases
                        trakt_lists, header = trakt.get(
                            'https://api.trakt.tv/movies/' + str(trakt_match.ids.trakt) + '/lists/personal/popular')
                        match = False
                        for trakt_list in trakt_lists:
                            if regex.search(r'(latest|new).*?(releases)', trakt_list.name, regex.I):
                                match = True
                        # if release_date and delay have passed or the movie was released early
                        return datetime.datetime.utcnow() > datetime.datetime.strptime(release_date,
                                                                                        '%Y-%m-%d') or match
                    elif trakt_match.type == 'season':
                        return datetime.datetime.utcnow() > datetime.datetime.strptime(trakt_match.first_aired,
                                                                                        '%Y-%m-%dT%H:%M:%S.000Z')
                    elif trakt_match.type == 'episode':
                        return datetime.datetime.utcnow() > datetime.datetime.strptime(trakt_match.first_aired,
                                                                                        '%Y-%m-%dT%H:%M:%S.000Z')
                except:
                    return False
        elif self.type == 'movie':
            released = datetime.datetime.today() - datetime.datetime.strptime(self.originallyAvailableAt,
                                                                                '%Y-%m-%d')
            if released.days < 0:
                return False
        return True

    def watched(self):
        import content.services.plex as plex
        import content.services.trakt as trakt
        import content.services.overseerr as overseerr
        if library.active == ['Plex Library']:
            try:
                if self.type == 'movie' or self.type == 'episode':
                    if hasattr(self, 'viewCount'):
                        if self.viewCount > 0:
                            if not self in plex.ignored:
                                plex.ignored += [self]
                            return True
                else:
                    if hasattr(self, 'viewedLeafCount'):
                        if self.viewedLeafCount >= self.leafCount:
                            if not self in plex.ignored:
                                plex.ignored += [self]
                            return True
                return False
            except Exception as e:
                ui_print("plex error: (attr exception): " + str(e), debug=ui_settings.debug)
                return False
        elif library.active == ['Trakt Collection']:
            return False

    def collected(self, list):
        import content.services.plex as plex
        import content.services.trakt as trakt
        import content.services.overseerr as overseerr
        if self.watchlist == plex.watchlist and library.active == ['Plex Library']:
            try:
                if self.type == 'show' or self.type == 'season':
                    match = next((x for x in list if x == self), None)
                    if not hasattr(match, 'leafCount'):
                        return False
                    if match.leafCount == self.leafCount:
                        return True
                    return False
                else:
                    return self in list
            except Exception as e:
                ui_print("plex error: (plex to plex library check exception): " + str(e), debug=ui_settings.debug)
                return False
        elif self.watchlist == trakt.watchlist and library.active == ['Plex Library']:
            try:
                if self.type in ['movie', 'show']:
                    if hasattr(self.ids, 'imdb'):
                        result = plex.match("imdb-" + self.ids.imdb, self.type, library=list)
                    elif hasattr(self.ids, 'tmdb'):
                        result = plex.match("tmdb-" + str(self.ids.tmdb), self.type, library=list)
                    elif hasattr(self.ids, 'tvdb'):
                        result = plex.match("tvdb-" + str(self.ids.tvdb), self.type, library=list)
                    if hasattr(self, 'Seasons'):
                        for season in self.Seasons:
                            matching_season = next((x for x in result[0].Seasons if x.index == season.index), None)
                            if hasattr(matching_season, 'viewedLeafCount'):
                                season.viewedLeafCount = matching_season.viewedLeafCount
                            if hasattr(matching_season, 'ratingKey'):
                                season.ratingKey = matching_season.ratingKey
                            season.parentGuid = result[0].guid
                            for episode in season.Episodes:
                                if hasattr(matching_season, 'Episodes'):
                                    matching_episode = next(
                                        (x for x in matching_season.Episodes if x.index == episode.index), None)
                                    if hasattr(matching_episode, 'viewCount'):
                                        episode.viewCount = matching_episode.viewCount
                                    if hasattr(matching_episode, 'ratingKey'):
                                        episode.ratingKey = matching_episode.ratingKey
                                episode.grandparentGuid = result[0].guid
                    if hasattr(result[0], 'viewCount'):
                        self.viewCount = result[0].viewCount
                    if hasattr(result[0], 'viewedLeafCount'):
                        self.viewedLeafCount = result[0].viewedLeafCount
                    if hasattr(result[0], 'ratingKey'):
                        self.ratingKey = result[0].ratingKey
                    return media.collected(result[0], list)
                elif self.type == 'season':
                    match = next((x for x in list if x == self), None)
                    if not hasattr(match, 'leafCount'):
                        return False
                    if match.leafCount == self.leafCount:
                        return True
                    return False
                elif self.type == 'episode':
                    return self in list
            except Exception as e:
                ui_print("trakt error: (trakt to plex library check exception): " + str(e), debug=ui_settings.debug)
                return False
        elif self.watchlist == trakt.watchlist and library.active == ['Trakt Collection']:
            try:
                if self.type == 'show' or self.type == 'season':
                    match = next((x for x in list if x == self), None)
                    if not hasattr(match, 'leafCount'):
                        return False
                    if match.leafCount == self.leafCount:
                        return True
                    return False
                else:
                    return self in list
            except Exception as e:
                ui_print("trakt error: (trakt to trakt library check exception): " + str(e),
                            debug=ui_settings.debug)
                return False
        elif self.watchlist == plex.watchlist and library.active == ['Trakt Collection']:
            try:
                if self.type in ['movie', 'show']:
                    for guid in self.Guid:
                        service, guid = guid.id.split('://')
                        trakt_match = trakt.match(guid, service, self.type)
                        if trakt_match:
                            break
                    if hasattr(self, 'Seasons'):
                        for season in self.Seasons:
                            season.parentGuid = trakt_match.guid
                            for episode in season.Episodes:
                                episode.grandparentGuid = trakt_match.guid
                        self.seasons = trakt_match.Seasons
                    self.ids = trakt_match.ids
                    return media.collected(trakt_match, list)
                elif self.type == 'season':
                    match = next((x for x in list if x == self), None)
                    if not hasattr(match, 'leafCount'):
                        return False
                    if match.leafCount == self.leafCount:
                        return True
                    return False
                else:
                    return self in list
            except Exception as e:
                ui_print("trakt error: (plex to trakt library check exception): " + str(e), debug=ui_settings.debug)
                return False
        else:
            ui_print("library check error: (no library check performed): " + str(e), debug=ui_settings.debug)
            return False

    def uncollected(self, list):
        if self.type == 'movie':
            if not self.collected(list):
                return [self]
        elif self.type == 'show':
            if self.collected(list) and not self.version_missing():
                return []
            Seasons = copy.deepcopy(self.Seasons)
            for season in Seasons[:]:
                if (not season.collected(list) or season.version_missing()) and not season.watched() and season.released() and not season.downloading():
                    for episode in season.Episodes[:]:
                        if (episode.collected(list) and not episode.version_missing()) or episode.watched() or not episode.released() or episode.downloading():
                            season.Episodes.remove(episode)
                else:
                    if season in Seasons:
                        Seasons.remove(season)
                if len(season.Episodes) == 0 and season in Seasons:
                    Seasons.remove(season)
            return Seasons
        return []

    def downloading(self):
        if hasattr(self, "version"):
            return [self.query() + ' [' + self.version.name + ']'] in debrid.downloading
        else:
            return False

    def download(self, retries=0, library=[], parentReleases=[]):
        import content.services.plex as plex
        import content.services.trakt as trakt
        import content.services.overseerr as overseerr
        current_module = sys.modules[__name__]
        refresh = False
        i = 0
        self.Releases = []
        if self.type == 'movie':
            if len(self.uncollected(library)) > 0 or (
                    len(self.versions()) > 0 and not len(self.versions()) == len(releases.sort.versions)):
                if self.released() and not self.watched() and not self.downloading():
                    tic = time.perf_counter()
                    alternate_years = [self.year, self.year - 1, self.year + 1]
                    for year in alternate_years:
                        i = 0
                        while len(self.Releases) == 0 and i <= retries:
                            self.Releases += scraper.scrape(self.query().replace(str(self.year), str(year)),
                                                        self.deviation())
                            i += 1
                        if not len(self.Releases) == 0:
                            self.year = year
                            break
                    debrid_downloaded, retry = self.debrid_download()
                    if debrid_downloaded:
                        refresh = True
                        if not retry and (
                                self.watchlist.autoremove == "both" or self.watchlist.autoremove == "movie"):
                            self.watchlist.remove([], self)
                        toc = time.perf_counter()
                        ui_print('took ' + str(round(toc - tic, 2)) + 's')
                    if retry:
                        self.watch()
        elif self.type == 'show':
            if self.released() and (not self.collected(library) or self.version_missing()) and not self.watched():
                self.Seasons = self.uncollected(library)
                # if there are uncollected episodes
                if len(self.Seasons) > 0:
                    tic = time.perf_counter()
                    # if there is more than one uncollected season
                    if len(self.Seasons) > 1:
                        self.Releases += scraper.scrape(self.query(), self.deviation())
                        parentReleases = copy.deepcopy(self.Releases)
                        # if there are more than 3 uncollected seasons, look for multi-season releases before downloading single-season releases
                        if len(self.Seasons) > 3:
                            # gather file information on scraped, cached releases
                            debrid.check(self)
                            multi_season_releases = []
                            season_releases = [None] * len(self.Seasons)
                            minimum_episodes = len(self.files()) / 2
                            season_queries = []
                            for season in self.Seasons:
                                season_queries += [season.deviation()]
                            season_queries_str = '(' + ')|('.join(season_queries) + ')'
                            for release in self.Releases:
                                match = regex.match(season_queries_str, release.title, regex.I)
                                for version in release.files:
                                    if isinstance(version.wanted, int):
                                        # if a multi season pack contains more than half of all uncollected episodes, accept it as a multi-season-pack.
                                        if version.wanted > minimum_episodes:
                                            multi_season_releases += [release]
                                            break
                                            # if the release is a single-season pack, find out the quality
                                        if match:
                                            for index, season_query in enumerate(season_queries):
                                                if regex.match(season_query, release.title, regex.I):
                                                    if version.wanted >= len(self.Seasons[index].files()) and \
                                                            season_releases[index] == None:
                                                        quality = regex.search('(2160|1080|720|480)(?=p|i)',
                                                                                release.title, regex.I)
                                                        if quality:
                                                            quality = int(quality.group())
                                                        else:
                                                            quality = 0
                                                        season_releases[index] = quality
                                                        break
                            # if there are eligible multi-season packs
                            if len(multi_season_releases) > 0:
                                download_multi_season_release = False
                                # if one of the shows seasons cant be downloaded as a single-season pack, download the multi-season pack.
                                for season_release in season_releases:
                                    if season_release == None:
                                        download_multi_season_release = True
                                        break
                                # if all seasons of the show could also be downloaded as single-season packs, compare the quality of the best ranking multi season pack with the lowest quality of the single season packs.
                                if not download_multi_season_release:
                                    season_quality = min(season_releases)
                                    quality = regex.search('(2160|1080|720|480)(?=p|i)',
                                                            multi_season_releases[0].title, regex.I)
                                    if quality:
                                        quality = int(quality.group())
                                    else:
                                        quality = 0
                                    if quality >= season_quality:
                                        download_multi_season_release = True
                                # if either not all seasons can be downloaded as single-season packs or the single season packs are of equal or lower quality compared to the multi-season packs, download the multi season packs.
                                if download_multi_season_release:
                                    self.Releases = multi_season_releases
                                    debrid_downloaded, retry = self.debrid_download()
                                    if debrid_downloaded:
                                        refresh = True
                                        if not retry:
                                            for season in self.Seasons[:]:
                                                for episode in season.Episodes[:]:
                                                    for file in self.Releases[0].files:
                                                        if hasattr(file, 'match'):
                                                            if file.match == episode.files()[0]:
                                                                season.Episodes.remove(episode)
                                                                break
                                                if len(season.Episodes) == 0:
                                                    self.Seasons.remove(season)
                    # Download all remaining seasons by starting a thread for each season.
                    results = [None] * len(self.Seasons)
                    threads = []
                    # start thread for each season
                    for index, Season in enumerate(self.Seasons):
                        t = Thread(target=download, args=(Season, library, parentReleases, results, index))
                        threads.append(t)
                        t.start()
                    # wait for the threads to complete
                    for t in threads:
                        t.join()
                    retry = False
                    for index, result in enumerate(results):
                        if result[0]:
                            refresh = True
                        if result[1]:
                            retry = True
                    if not retry and (self.watchlist.autoremove == "both" or self.watchlist.autoremove == "show"):
                        self.watchlist.remove([], self)
                    toc = time.perf_counter()
                    ui_print('took ' + str(round(toc - tic, 2)) + 's')
        elif self.type == 'season':
            altquery = self.deviation()
            for release in parentReleases:
                if regex.match(r'(' + altquery + ')', release.title, regex.I):
                    self.Releases += [release]
            if not len(self.Episodes) <= self.leafCount / 2:
                debrid_downloaded, retry = self.debrid_download()
                if debrid_downloaded:
                    return True, retry
                else:
                    self.Releases = []
                while len(self.Releases) == 0 and i <= retries:
                    self.Releases += scraper.scrape(self.query(), self.deviation())
                    i += 1
            debrid_downloaded, retry = self.debrid_download()
            if not debrid_downloaded or retry:
                self.Releases += scraper.scrape(self.query()[:-1])
                for episode in self.Episodes:
                    downloaded, retry = episode.download(library=library, parentReleases=self.Releases)
                    if downloaded:
                        refresh = True
                    if retry:
                        episode.watch()
                if refresh:
                    return True, retry
                return False, retry
            else:
                return True, retry
        elif self.type == 'episode':
            while len(self.Releases) == 0 and i <= retries:
                altquery = self.deviation()
                for release in parentReleases:
                    if regex.match(r'(' + altquery + ')', release.title, regex.I):
                        self.Releases += [release]
                debrid_downloaded, retry = self.debrid_download()
                if debrid_downloaded:
                    return True, retry
                else:
                    self.Releases = scraper.scrape(self.query(), self.deviation())
                i += 1
            return self.debrid_download()
        if refresh and current_module.library.active == [plex.library.name]:
            if self.type == 'movie':
                plex.library.refresh(plex.library.movies)
            elif self.type == 'show':
                plex.library.refresh(plex.library.shows)
            return True
        elif refresh and current_module.library.active == [trakt.library.name]:
            trakt.library.add(self)

    def downloaded(self):
        media.downloaded_versions += [self.query() + ' [' + self.version.name + ']']
        if self.type == 'show':
            for season in self.Seasons:
                season.version = self.version
                season.downloaded()
        if self.type == 'season':
            for episode in self.Episodes:
                episode.version = self.version
                episode.downloaded()

    def debrid_download(self):
        debrid.check(self)
        scraped_releases = copy.deepcopy(self.Releases)
        downloaded = []
        if len(scraped_releases) > 0:
            for version in self.versions():
                debrid_uncached = True
                for rule in version.rules:
                    if rule[0] == "cache status" and rule[1] == 'requirement' and rule[2] == "cached":
                        debrid_uncached = False
                self.version = version
                self.Releases = copy.deepcopy(scraped_releases)
                releases.sort(self.Releases, self.version)
                if debrid.download(self, stream=True):
                    self.downloaded()
                    downloaded += [True]
                elif not self.type == 'show' and debrid_uncached:  # change to version definition of cache status
                    if debrid.download(self, stream=False):
                        self.downloaded()
                        debrid.downloading += [self.query() + ' [' + self.version.name + ']']
                        downloaded += [True]
                    else:
                        downloaded += [False]
                else:
                    downloaded += [False]
        return True in downloaded, (False in downloaded or len(downloaded) == 0)

    def files(self):
        files = []
        if self.type == 'movie':
            files = [self.query()]
        elif self.type == 'show':
            for season in self.Seasons:
                for episode in season.Episodes:
                    files += episode.files()
        elif self.type == 'season':
            for episode in self.Episodes:
                files += episode.files()
        elif self.type == 'episode':
            files += ['S' + str("{:02d}".format(self.parentIndex)) + 'E' + str("{:02d}".format(self.index)) + '']
        return files

# Multiprocessing download method
def download(cls, library, parentReleases, result, index):
    result[index] = cls.download(library=library, parentReleases=parentReleases)
