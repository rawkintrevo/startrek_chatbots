
from HTMLParser import HTMLParser
from requests import get

import os

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

class DataFetcher:

    def __init__(self):
        self.base_urls = ["http://www.chakoteya.net/NextGen/episodes.htm",
                     "http://www.chakoteya.net/DS9/episodes.htm",
                     "http://www.chakoteya.net/Voyager/episode_listing.htm",
                     "http://www.chakoteya.net/Enterprise/episodes.htm",
                     "http://www.chakoteya.net/movies/index.htm",
                     "http://www.chakoteya.net/StarTrek/episodes.htm"
                     ]

    def strip_tags(self, html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

    def processWebPage(self, html):
        if "tbody" in html:
            # title = strip_tags(html.split('tbody')[0]).split( "-")[1].split('\n')[0].strip()
            body = "".join([c for c in self.strip_tags(html.split('tbody')[1]).replace("\r", '').replace(u"\ufffd", '') if ord(c) < 128])
            output = body #
            return output
        if "CREDIT" in html:
            script = self.strip_tags(html.split("CREDIT")[1]).replace(u'\ufffd', '')
            return script
        else:
            print("not sure how to parse this one...")

    def downloadScripts(self, outputdir, overwrite= False):
        for bu in self.base_urls:
            r = get(bu)
            print(bu)
            pages = [line.split('"')[0] for line in r.text.split('href="') if line.split('"')[0][0].isdigit() or line.split('"')[0][0] == 'm' ]
            series_name = bu.split("/")[-2]
            base_path = "/".join(bu.split("/")[:-1])
            directory = outputdir + "/" + series_name + "/"
            for p in pages:
                print(p)
                if os.path.exists(directory + p.split(".")[0] + ".txt"):
                    if not overwrite:
                        continue
                r = get(base_path + "/" + p)
                out = self.processWebPage(r.text)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                with open(directory + p.split(".")[0] + ".txt", 'wb') as f:
                    f.write(out)
