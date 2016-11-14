from config import myshows
from tpb import TPB
from tpb import  CATEGORIES, ORDERS
import mag2file as m2f
import trakt
import trakt.tv as ttv
import trakt.users as users
from trakt import init
from imdbpie import Imdb
from collections import OrderedDict
from datetime import datetime as DT
import datetime
from Objects import mySeason

imdb = Imdb()
today = DT.now()
trakt.AUTH_METHOD = trakt.OAUTH_AUTH
init("thehalk",
     "e99449458e449cca25136bab23f02ea62ed4ae40d290c5b0e08e68947f8c6ed8",
      "fdd36a986b1c4763ab5ed2cd7cec0698a1b62aaa0bc349da36792a621d9fd82f")

myuser = users.User("thehalk")



def getNumberOfEpisodes(show):
    total = 0
    for season in show.seasons:
        try:
            total += season['episodes'].__len__()
        except:
            total += season.aired_episodes
    return total

def getWatchedEpisodes(myshow):
    watched = OrderedDict()
    for season in myshow.seasons:
        s = mySeason(myshow.seasons.index(season)+1)
        for epi in season['episodes']:
            s.addEpisode(epi['number'])
        watched[s.season] = s
    return watched

def getAiredEpisodes(myshow):
    def getReleaseDate(e, es):
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
    s = mySeason(1)
    episodes = imdb.get_episodes(myshow.imdb)
    for epi in episodes:
        if epi.release_date is None:
            # if "pilot" in epi.title.lower(): continue
            _rdate = getReleaseDate(epi,episodes)
        else: _rdate = epi.release_date
        try:
            rdate = DT.strptime(_rdate, "%Y-%m-%d")
        except:
            rdate = DT.strptime(u'2100-01-01', "%Y-%m-%d")
        if today >= rdate:
            if epi.season == s.season:
                s.addEpisode(epi.episode)
            else:
                aired[s.season] = s
                s = mySeason(epi.season)
                s.addEpisode(epi.episode)
        else:
            break
    aired[s.season] = s
    return aired

def diffEpisodes(wholeDict, partialDict):
    diff_total = OrderedDict()
    for i in range(1,wholeDict.__len__()+1):
        s = mySeason(i)
        epi_diff = list(set(wholeDict[i].episodes) - set(partialDict[i].episodes))
        if epi_diff != []:
            for epi in epi_diff: s.addEpisode(epi)
            diff_total[s.season] = s

    return diff_total

for show in myuser.watched_shows:
    watchedEpisodes = getWatchedEpisodes(show)
    airedEpisodes = getAiredEpisodes(show)

    diffEpi = diffEpisodes(airedEpisodes, watchedEpisodes)
    continue
    title = imdb.get_title_by_id(show.imdb)
    epi = imdb.get_episodes(show.imdb)
    # print show.title
    for a in ttv.search(show.title, 'show'):
        if a.ext == show.ext:
            _show = a
            break
    if _show.status == u'returning series' and _show.seasons[-1].aired_episodes != 0:
        _watched = getNumberOfEpisodes(show)
        _total = getNumberOfEpisodes(_show)
        print show.title,
        print "Watched: " + str(_watched),
        print "Total: " + str(_total)
        if _watched <> _total:
            print unicode(_show.seasons[-1].number) + " : " + unicode(_show.seasons[-1].aired_episodes)
exit()
try:
    for show in myshows:
        # print show
        _show = ttv.TVShow(show)
        if _show.status == u'returning series' and _show.seasons[-1].aired_episodes != 0:
            print show,
            print unicode(_show.seasons[-1].number) + " : " + unicode(_show.seasons[-1].aired_episodes)
except:
    print show
    raise

exit()
t = TPB("http://thepiratebay.org")

def mag2file(mag, ofile):
    m2f.magnet2torrent(mag, ofile)

search = t.search("Legends of Tomorrow", category=CATEGORIES.VIDEO)

for tor in search:
    print tor
