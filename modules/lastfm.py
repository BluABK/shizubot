__author__ = 'BluABK <abk@blucoders.net'

# This module requires pylast to be installed https://github.com/pylast/pylast
import pylast
import ConfigParser
import os
import re, cgi

class Config:  # Shizu's config class
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        self.config.read(os.getcwd() + '/' + "config.ini")

    def loadconfig(self):
        configloc = os.getcwd() + '/' + "config.ini"
        print(configloc)
        self.config.read(configloc)
        return True

    def api_key(self):
        return str(self.config.get('lastfm', 'api-key'))

    def api_secret(self):
        return str(self.config.get('lastfm', 'api-secret'))

    def username(self):
        return str(self.config.get('lastfm', 'username'))

    def password(self):
        return str(self.config.get('lastfm', 'password'))

    def password_hash(self):
        return str(self.config.get('lastfm', 'password_hash'))

    def test_alias(self, user):
        if str(self.config.get('lastfm', 'username')) == user:
            return str(self.config.get('lastfm', 'username'))
        else:
            try:
                return str(self.config.get('lastfm-alias', user))
            except ConfigParser.NoOptionError:
                return None

cfg = Config()
commandsavail_short = "np, npt"
commandsavail = "imaginary, recent*"
network = pylast.LastFMNetwork(api_key=cfg.api_key(), api_secret=cfg.api_secret(),
                               username=cfg.username(), password_hash=cfg.password_hash())


def test_playing(user):
    try:
        return network.get_user(user).get_now_playing()
    except pylast.WSError:
        return "No user with that name was found"


def format_basic(li):
    f_li = list()
    for track in li:
        unicode_track = unicode(str(track.track), 'utf8')
        f_li.append((track.playback_date + "\t" + unicode_track).encode('utf-8'))
        # Debug print
        print (track.playback_date + "\t" + unicode_track).encode('utf-8')
    return f_li


def strip_biojunk(string):
    newstring = ""
    for char in string:
        # 512 bytes is more than enough of a summary (amount takes sendmsg() into account
        if newstring.__sizeof__() > 493:
            newstring += "..."
            break
        # "read more..." and other junk usually happens after a few newlines
        if char == "\n":
            newstring += "..."
            break
        else:
            newstring += char
    return newstring


def strip_html(data):
    tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')

    # Remove well-formed tags, fixing mistakes by legitimate users
    no_tags = tag_re.sub('', data)

    # Clean up anything else by escaping
    return cgi.escape(no_tags)


def now_playing(user):
    try:
        u = cfg.test_alias(user)
        if u is None:
            u = user
        return network.get_user(u).get_now_playing()
    except pylast.WSError:
        return None


def recently_played(user, num):
    try:
        u = cfg.test_alias(user)
        if u is None:
            u = user
        rplist = network.get_user(u).get_recent_tracks(limit=num)
#    except pylast.WSError.details == "Rate limit exceeded":
#        return "Rate limit exceeded o0"
    except pylast.WSError:
        #err = "No user with that name was found"
        return None

    return format_basic(rplist)


def artist_bio(name):
    try:
        data = network.get_artist(name).get_bio_summary()
    except AttributeError:
        data = "Ouch, attribute error. Did you try something nasty?"
        return data
    except pylast.WSError:
        data = "There was an error or some shit, happy now SpyTec?"
        return data
    data = strip_html(data).encode('utf-8')
    try:
        data = strip_biojunk(data)
    except AttributeError:
        data = "Ouch, attribute error. Did you try something nasty?"
        return data
    print data
    return data


def helpcmd(cmdsym):
    cmdlist = list()
    cmdlist.append("Syntax: %scommand help arg1..argN" % cmdsym)
    cmdlist.append("Available commands: %s (* command contains sub-commands)" % commandsavail_short)
    cmdlist.append("Syntax: %slastfm help arg1..argN" % cmdsym)
    cmdlist.append("Available commands: %s (* command contains sub-commands)" % commandsavail)
    return cmdlist