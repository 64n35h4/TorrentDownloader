# TorrentDownloader
TorrentDownloader is a download tool for torrent files - __Version 1.0, STILL HAS BUGS!__ - Work In Progress.

This tool will scan your watched history from trakt website, compare it to the currently aired episodes of each show, and compare that to the files you already downloaded onto your computer - if there will be any episodes aired that you havn't seen and didn't download already - it will search them on ThePirateBay and download them for you.

* Update the watchlist shows on shows.py (assuming you don't have to search all your trakt history - time consuming)
* Each show folder should be labeled with the show name as shown on trakt website - format and names of the files inside that folder doesn't matter 

It requires 2 accounts:
  1. Trakt account: https://trakt.tv and to setup and APP key and secret - this will let you track your show seen episodes
  2. TMDB account: https://www.themoviedb.org/ and to setup and API key - this will let you obtain show air detailed (more accurate than IMDB)
  
Place the relevent data in the config.ini file
