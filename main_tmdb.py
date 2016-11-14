import os
import sys
from shows import watchlist
from tpb import TPB
from tpb import  CATEGORIES, ORDERS
import trakt
import trakt.tv as ttv
import trakt.users as users
from trakt import init
from collections import OrderedDict
from datetime import datetime as DT
import datetime
import tmdbsimple as tmdb
from Objects import mySeason
from extract_existing_files import scanPresentFiles, slugifyFolders
import ConfigParser
from time import sleep

#------------------------------------ Init -------------------------------------
config = ConfigParser.ConfigParser()
# reading config file
config.read('config.ini')
today = DT.now()
trakt.AUTH_METHOD = trakt.OAUTH_AUTH
init(config.get("trakt","user"),config.get("trakt","app_id"),config.get("trakt","app_secret"))

tmdb.API_KEY = config.get("tmdb","api_key")
myuser = users.User(config.get("tmdb","user"))
BASE_URL = config.get("main","path")

#---------------------------------------------------------------------------------
#slugify folders for more robust
slugifyFolders(BASE_URL)
print "Finished slugifying folders"

def getWatchedEpisodes(myshow):
    """
    getting watched episodes from trakt API
    :param myshow: which show
    :return: OrderedDict of watched episodes and seasons
    """
    watched = OrderedDict()
    for season in myshow.seasons:
        s = mySeason(myshow.seasons.index(season)+1)
        for epi in season['episodes']:
            s.addEpisode(epi['number'])
        watched[s.season] = s
    return watched

def getAiredEpisodesTMDB(myshow):
    """
    Getting Aired Episodes by date from TMDB
    """
    def getReleaseDate(e, es):
        """
        Getting Release date - if not present, find next episode that has release date, and subtract no. of episode * 7 days backwards #TODO: Improve?
        If can't find any date, return future date.
        """
        index = es.index(e)+1
        while True:
            if index < es.__len__():
                if es[index].release_date is not None:
                    dtObj = DT.strptime(es[index].release_date, "%Y-%m-%d")
                    cor_dtObj = dtObj - datetime.timedelta(days=7*index)
                    return DT.strftime(cor_dtObj, "%Y-%m-%d")
                else:
                    index +=1
            else:
                print "Cannot find release date in all the episodes"
                return u'2100-01-01'

    aired = OrderedDict()
    _seasons = tmdb.TV(myshow.tmdb).info()['seasons']
    _seasons = [cell for cell in _seasons if (cell['season_number'] != 0 and cell['season_number'] is not None)]
    for i in range(0, _seasons.__len__()):
        if _seasons[i]['episode_count'] == 0: continue
        _episodes = tmdb.TV_Seasons(myshow.tmdb, _seasons[i]['season_number']).info()['episodes']
        s = mySeason(i+1)
        for epi in _episodes:
            if epi['air_date'] is None:
                _rdate = getReleaseDate(epi, _episodes)
            else:
                _rdate = epi['air_date']
            try:
                rdate = DT.strptime(_rdate, "%Y-%m-%d")
            except:
                rdate = DT.strptime(u'2100-01-01', "%Y-%m-%d")
            if today >= rdate:
                s.addEpisode(epi['episode_number'])
            else:
                break
        if s.episodes != []:
            aired[s.season] = s
    return aired

def diffEpisodes(sh,wholeDict, partialDict):
    """
    Getting diff between aired episodes and watched episodes
    Assuming that aired array >= watched array
    """
    for s_diff in list(set(wholeDict.keys()) - set(partialDict.keys())):
        s_diff_obj = mySeason(s_diff)
        partialDict[s_diff_obj.season] = s_diff_obj
    diff_total = OrderedDict()

    for i in wholeDict.keys():
        s = mySeason(i)
        epi_diff = list(set(wholeDict[i].episodes) - set(partialDict[i].episodes))
        if epi_diff != []:
            for epi in epi_diff: s.addEpisode(epi)
            diff_total[s.season] = s

    return diff_total

EpisodesToDownload = {}

# going over all watched shows from trakt API
for show in myuser.watched_shows:
    # if show not in watchlist - skip
    if show.title not in watchlist:
        continue
    print "Getting watched episodes for show: {}".format(show.title)
    watchedEpisodes = getWatchedEpisodes(show)
    print "Getting which episodes aired for show: {}".format(show.title)
    airedEpisodes = getAiredEpisodesTMDB(show)
    print "Getting diff episodes for show: {}".format(show.title)
    diffEpi = diffEpisodes(show,airedEpisodes, watchedEpisodes)

    if bool(diffEpi):
        # if there is diff - scan all present downloaded files (prevent duplicates)
        presentEpisodes = scanPresentFiles(BASE_URL, ttv.slugify(show.title))
        # get new diff of old_diff and that present files that on your computer
        diffPresent = diffEpisodes(show, diffEpi, presentEpisodes)
        if bool(diffPresent):
            # if there are files to download that you havn't already downloaded - add to download dict
            print "\t\tAdding show {} to dict".format(show.title)
            EpisodesToDownload[show.title] = diffPresent

# Start of TBP API
t = TPB("http://thepiratebay.org")

# list of valid publishers - don't want any torrent from anyone..
validPublishers = ['ettv','LOL','FUM','DIMENSION','KILLERS','FLEET', 'AFG']

print
print "I'm going to download the following shows and episodes:"

# go over all the "to download" shows
for _show,season in EpisodesToDownload.items():
    print _show,
    for entry in season.values():
        s = "0"+str(entry.season) if len(str(entry.season)) == 1 else str(entry.season)
        episodes = entry.episodes
        for e in episodes:
            e = "0" + str(e) if len(str(e)) == 1 else str(e)
            print "S{}E{}".format(s,e)
            search_term = "{} S{}E{}".format(_show,s,e)
            # built a search_term, execute on API, on TV_SHOWS catagory, ordering by seeding (higher first)
            _search = TPB("http://thepiratebay.org").search(search_term, category=CATEGORIES.VIDEO.TV_SHOWS).order(ORDERS.SEEDERS.DES)
            for tor in _search:
                if any(ext in tor.title for ext in validPublishers):
                    print "Downadling: " + tor.title
                    print "To: " + BASE_URL

                    # Starting torrent link in torrent client (Windows) - #TODO: Linux compatability?
                    os.startfile(tor.magnet_link)
                    # sleep to avoid DOS on gateway?
                    sleep(15)
                    break
        print
