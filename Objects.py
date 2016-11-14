class mySeason(object):
    def __init__(self,Season):
        self.season = Season
        self.episodes = []

    def addEpisode(self,Episode):
        self.episodes.append(Episode)

    def getData(self):
        return {
            'Season'    : self.season,
            'Episodes'  : self.episodes
        }