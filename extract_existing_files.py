import os
import re
from collections import OrderedDict
from Objects import mySeason
from trakt.tv import slugify
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('config.ini')

BASE_URL = config.get("main","path")

def getEpisodeNumberNSeason(filename):
    match = re.search(
        r'''\W[sS]\d*[eE]\d*\W|\W\d\d+\W|\W\d+[xX]\d+\W''', filename)
    if match:
        s,e = 0,0
        m = match.group(0).lower().strip()
        if m.startswith("."): m = m[1:]
        if m.endswith("."): m = m[:-1]
        if 'x' in m: m = m.replace("x","")
        if len(m) == 3:
            s = "0" + m[0]
            e = m[1:]
        if len(m) == 4:
            s = m[:2]
            e = m[2:]
        if m.startswith('s'):
            m = m[1:]
            if 'e' in m:
                m = m.split('e')
                s = m[0]
                e = m[1]
            else:
                s = m[:2]
                e = m[3:]
        return [s, e]

def slugifyFolders(BASE=None):
    for dir in [c for c in os.listdir(BASE_URL) if os.path.isdir(os.path.join(BASE_URL, c))]:
        os.rename(os.path.join(BASE_URL,dir), os.path.join(BASE_URL,slugify(dir)))

def scanPresentFiles(BASE_URL=os.path.dirname(os.path.realpath(__file__)), dir=""):
    valid = ["mp4","avi","mkv"]
    dir_key = slugify(dir)
    hasEpidsodes = OrderedDict()
    try:
        for f in os.listdir(os.path.join(BASE_URL,dir)):
            if f.endswith(tuple(valid)):
                [s,e] = getEpisodeNumberNSeason(f)
                if int(s) in hasEpidsodes.keys():
                    hasEpidsodes[int(s)].addEpisode(int(e))
                else:
                    hasEpidsodes[int(s)] = mySeason(int(s))
                    hasEpidsodes[int(s)].addEpisode(int(e))
    except WindowsError:
        pass
    return hasEpidsodes

if __name__ == "__main__":
    scanPresentFiles(BASE_URL)
