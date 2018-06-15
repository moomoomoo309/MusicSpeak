#!/usr/bin/env python

# Dependencies: pympris
# Tested on Python 2.7 and 3.6. Will probably work as long as you have str.format and pympris.

from os import system as runCommand
from time import sleep
from collections import namedtuple
from datetime import datetime
from argparse import ArgumentParser
from dbus import DBusException

from pympris import available_players
from pympris.MediaPlayer import MediaPlayer
from pympris.common import PyMPRISException

# The TTS I used is available at https://github.com/Glutanimate/simple-google-tts
# At the time of writing, it is unmaintained, but still works.
# This is easily replaceable with a TTS program of your choice.
# I put pico2wave as the default, since it works well and is maintained.
parser = ArgumentParser()

TTSProgram = u"pico2wave -w=/tmp/tts.wav \"{phrase}\"; aplay /tmp/tts.wav -q; rm /tmp/tts.wav"
voiceFormatStr = u"Playing {artist}'s '{song}' from '{album}'"
dtFormatStr = u"%Y-%M-%d@%I:%M.%S%p"

parser.add_argument(u"--tts", dest=u"TTSProgram", help=u"The program used to output the speech. Use {phrase} to "
                                                       u"specify where the phrase to speak will be placed.")
parser.add_argument(u"--format", dest=u"voiceFormatStr", help=u"The format string used to specify what will be said. "
                                                              u"The variables {artist}, {song}, and {album} will be "
                                                              u"replaced.")
parser.add_argument(u"--dtFormat", dest=u"dtFormatStr", help=u"The datetime format string used by the program to log "
                                                             u"when the song changes.")
args = parser.parse_args()
TTSProgram = args.TTSProgram or TTSProgram
voiceFormatStr = args.voiceFormatStr or voiceFormatStr
dtFormatStr = args.dtFormatStr or dtFormatStr

SongData = namedtuple(u"SongData", (u"artist", u"album", u"title"))

players = []
lastSong = dict()
while True:
    try:
        del players[:]
        for playerName in available_players():
            players.append(MediaPlayer(playerName))
        for player in players:
            if player.player.PlaybackStatus == u"Playing":
                meta = player.player.Metadata
            else:
                continue  # Cuts down on the indentation.
            if u"xesam:artist" in meta and u"xesam:title" in meta and u"xesam:album" in meta:
                song = SongData(artist=meta[u"xesam:artist"], title=u"" + meta[u"xesam:title"],
                                album=u"" + meta[u"xesam:album"])
            else:
                continue  # Cuts down on the indentation.
            if player.player.name not in lastSong or song != lastSong[player.player.name]:
                lastSong[player.player.name] = song
                speakStr = voiceFormatStr.format(artist=u" and ".join(song.artist), song=song.title, album=song.album)
                print(u"[{}] {}".format(datetime.now().strftime(dtFormatStr), speakStr))
                player.player.Pause()
                runCommand(TTSProgram.format(phrase=speakStr))
                player.player.Play()
    except (DBusException, PyMPRISException):
        pass
    sleep(.05)
