import praw
from validators import url as validate
from whois import whois
from datetime import datetime
from os.path import isdir
from os import mkdir

logpath = "logs/"+str(datetime.now())+".log"

# all invalid response codes by the whois server
errors = None, "REDACTED FOR PRIVACY", "Statutory Masking Enabled", "DATA REDACTED", "Whois Privacy (enumDNS dba)", "Privacy service provided by Withheld for Privacy ehf"

# create logdir
if not isdir(logpath.split("/")[0]):
    mkdir(logpath.split("/")[0])


# login
reddit = praw.Reddit(
    client_id="CLIENT ID",
    client_secret="CLIENT SECRET",
    password="PASSWORD",
    user_agent="python:domainfo:v1.0 (by u/30p87)",
    username="USERNAME",
)


print(reddit.user.me())


# returns the first element of a list (which randomly appear in answers) - IF it's a list
def ltn(_v):
    if type(_v) == list:
        return(_v[0])
    return(_v)


# loops all comments of the comment stream of all subreddits
for comment in reddit.subreddit("all").stream.comments(skip_existing=True):
    if not comment.author == reddit.user.me():
        c = comment.body.split()    # splits the whole comment into single arguments
        if len(c) > 1:    # if it could hold the call (u/domaininfo) and a url
            if c[0] == reddit.user.me().name or c[0] == "u/" + reddit.user.me().name:    # checks if its just domainfo or u/domainfo, as thats for the bot
                c.pop(0)    # the call (u/...) isn't needed anymore
                _url = c[0]
                if validate(_url) or validate("https://"+_url) or validate("http://"+_url):    # checks if the second part is a url at all, including with adding https://
                    if not validate(_url):    # converts the url into a https://url
                        if validate("https://"+_url):
                            _url = "https://"+_url
                        elif validate("http://"+_url):
                            _url = "http://"+_url
                    try: _w = whois(c[0])    # makes the whois request, try must be as it throws exceptions when the registration is not found
                    except:
                        if _url.startswith("http"):    # forces the https:// away so namecheap can work with it (and it's nicer on the eyes)
                            _url2 = _url.split("//")[1]
                        msg = _url + " is not registered. Get it on [Namecheap - " + _url2 + "](https://www.namecheap.com/domains/registration/results/?domain=" + _url2 + ")"
                    else:
                        msg = _url + " is registered"    # the base msg. This could be a respone, if all data is not there/redacted/randomly missing.
                        _pos = ""    # a string that will hold the position (adress, zipcode city, state, country :: Ligma balls 69, 42069 Penistone, CA, US)
                        if not _w.org in errors:
                            msg += " by " + ltn(_w.org)
                        if not _w.registrar in errors:
                            msg += " via " + ltn(_w.registrar)
                        if not _w.address in errors:
                            _pos += " at " + ltn(_w.address) + ", "
                        if not _w.zipcode in errors:
                            if not _w.city in errors:
                                _pos += ltn(_w.zipcode)
                            else:
                                _pos += ltn(_w.zipcode) + ", "
                        if not _w.city in errors:
                            _pos += ltn(_w.city) + ", "
                        if not _w.state in errors:
                            _pos += ltn(_w.state) + ", "
                        if not _w.country in errors:
                            _pos += ltn(_w.country) + ", "
                        if not _pos == "":    # adds _pos to msg
                            _pos = _pos[:-2]    # takes away the last two chars (", ") as they're unwanted (like me)
                            if not _pos.startswith(" at"):    # if the adress is there it already has a prefix, "at", if not it needs "in"
                                msg += " in " + _pos
                            else:
                                msg += _pos
                        if not _w.creation_date in errors:
                            msg += " since " + str(ltn(_w.creation_date))
                        if not _w.expiration_date in errors:
                            msg += " till " + str(ltn(_w.expiration_date))
                        msg += "."

                    comment.reply(msg)    # finally reply's
                    _f = open(logpath, "a")    # opens, appends to, and closes the logfile
                    _f.write(f"{comment.author}:{comment.body}:{msg}\n")
                    _f.close()
