import random, string, tweepy

from datetime import datetime

from cli_chatbot import *
from lib.emojis import emojis
from twitter_creds import data, laforge, picard, narrator, riker, troi, worf


"""
We should be able to take a list of new tweets, for each tweet, assign to the correct conversation (or create a new 
conersation if it is a split). Then for each conversation, create the next line and tweet it out. 

Required Methods/Items:
[x] Tweets in conversation.
[x] List of Human Players unique to each conversation.
[x] Create a story from a list of tweets.
[x] Generate a 'next line'.
Convert a next line into a tweet format.
[x] Tweet the next line.
Determine if a tweet exists in or is a new tweet belonging to a given conversation. 
"""

class Conversation:

    def __init__(self):
        self.at_bot_players = { "@CmdrDataBot" : "Data",
                                "@BotLaforge"  : "LaForge",
                                "@BotPicard": "Picard",
                                "@BotRiker" : "Riker",
                                "@BotTroi"  : "Troi",
                               "@BotWorf"   : "Worf",
                               "@ST_NarratorBot": ""}
        self.bot_players = {   "CmdrDataBot" : "DATA",
                               "BotLaforge" : "LAFORGE",
                                "BotPicard": "PICARD",
                               "BotRiker"  : "RIKER",
                               "BotTroi"   : "TROI",
                              "BotWorf" : "WORF",
                              "ST_NarratorBot": ""}
        self.human_players = {
            # rawkintrevo : DATA
            }

        # self.human_players_rev = {
        #     # DATA : rawkintrevo
        # }

        data_auth = tweepy.OAuthHandler(data.consumer_key, data.consumer_secret)
        data_auth.set_access_token(data.access_token, data.access_token_secret)

        laforge_auth = tweepy.OAuthHandler(laforge.consumer_key, laforge.consumer_secret)
        laforge_auth.set_access_token(laforge.access_token, laforge.access_token_secret)

        picard_auth = tweepy.OAuthHandler(picard.consumer_key, picard.consumer_secret)
        picard_auth.set_access_token(picard.access_token, picard.access_token_secret)

        nar_auth = tweepy.OAuthHandler(narrator.consumer_key, narrator.consumer_secret)
        nar_auth.set_access_token(narrator.access_token, narrator.access_token_secret)

        riker_auth = tweepy.OAuthHandler(riker.consumer_key, riker.consumer_secret)
        riker_auth.set_access_token(riker.access_token, riker.access_token_secret)

        troi_auth = tweepy.OAuthHandler(troi.consumer_key, troi.consumer_secret)
        troi_auth.set_access_token(troi.access_token, troi.access_token_secret)

        worf_auth = tweepy.OAuthHandler(worf.consumer_key, worf.consumer_secret)
        worf_auth.set_access_token(worf.access_token, worf.access_token_secret)

        self.apis = {   "DATA"     : tweepy.API(data_auth),
                        "LAFORGE"  : tweepy.API(laforge_auth),
                        "PICARD"   : tweepy.API(picard_auth),
                        "RIKER"    : tweepy.API(riker_auth),
                        "TROI"     : tweepy.API(troi_auth),
                        "WORF"     : tweepy.API(worf_auth),
                        "narrator" : tweepy.API(nar_auth)}

        self.tweets_hx = []
        self.tweet_cache = {}
        #

    def find_ids_in_conversation(self, tweet):
        """
        Find all messages in conversation prior to this one
        :param tweet: a Tweepy Status
        :return: None updates self.tweets_in_conversation with a list of every tweet in conversation prior to given tweet
            ordered from oldest to newest. (e.g. passed tweet will be in the last position of the list)
        """
        print("building conversatoin")
        tweets_in_conversation = [tweet]
        while tweet.in_reply_to_status_id_str is not None:
            if tweet.in_reply_to_status_id_str in self.tweet_cache:
                tweet = self.tweet_cache[tweet.in_reply_to_status_id_str]
            else:
                tweet = self.apis['PICARD'].statuses_lookup([tweet.in_reply_to_status_id_str])[0]
                self.tweet_cache[tweet.id_str] = tweet
            if "The role of" in tweet.text and "will now be played by" in tweet.text:
                print("Found '%s' assigning human player" % tweet.text)
                script_name, screen_name = tweet.text.split("The role of")[1].split("will now be played by ")
                # self.human_players_rev[screen_name.replace("@", "").strip()] = script_name.strip()
                self.human_players[screen_name.replace("@", "").strip()] = script_name.strip()
                continue
            tweets_in_conversation.append(tweet)
            # if len(tweets_in_conversation) > 30:
            #     print("early terminating... we have 30 tweets in conversation now")
            #     break
        tweets_in_conversation.reverse()
        self.tweets_hx = tweets_in_conversation

    def get_new_tweets(self):
        """
        :return: A list of Tweepy statuses in descending order from newest to oldest. (Includes mentions and tweets by all bots)
        """
        from operator import itemgetter
        new_tweets = []
        for bot in self.apis.keys():
            print("Checking for new tweets on bot: %s" % bot)
            new_tweets = new_tweets + self.apis[bot].mentions_timeline() + self.apis[bot].user_timeline()
        sorted_tweets = [(m.id, m) for m in new_tweets]
        sorted_tweets.sort(key=itemgetter(0))
        sorted_tweets.reverse()
        new_mentions = [m[1] for m in sorted_tweets]
        return new_mentions

    def build_story(self):
        # will walk up ids_in_converation to build story, replacing all usernames with script names
        story = self._story_post_processing(" ".join([self._replace_screennames_with_script_names(m) for m in self.tweets_hx]))
        return " ".join(story.split()[-100:])

    def next_tweet(self):
        if self._wait_for_human():
            return
        story = self.build_story()
        tweet_text = get_new_script_line(story)
        speaker, line = self.prep_next_line_for_tweeting(tweet_text[0])
        if speaker == None:
            return
        if self.tweet(speaker, line, self.tweets_hx[-1].id):
            print("Tweet: SUCCESS")
        else:
            if len(tweet_text) > 1:
                speaker, line = self.prep_next_line_for_tweeting(tweet_text[1])
                self.tweet(speaker, line, self.tweets_hx[-1].id)


    ####################################################################################################################
    ### "Internal Story Buildling Methods"

    def _add_human_to_chars(self, human_sn):
        print("Adding '%s' to human_players" % human_sn)
        name = self._load_random_name()
        self.human_players[human_sn] = name
        # self.human_players_rev[human_sn] = name
        # tweet from ST_NarratorBot: "The role of _NAME_ will now be played by @whoever"
        self.tweet('narrator', "The role of %s will now be played by @%s" % (name, human_sn), self.tweets_hx[-1].id)


    def _convert_sn_to_script_name(self, sn):
        if sn == "ST_NarratorBot":
            return ""
        ## Check for BOT Players first
        if sn in self.bot_players:
            return "%s : " % self.bot_players[sn]
        if sn in self.human_players:
            print("'%s' is being played by '%s'" % (self.human_players[sn], sn))
            return "%s : " % self.human_players[sn]
        print("ruh roh- %s is neither human nor bot..." % sn)

    def _ensure_sn_exists(self, sn):
        """
        Make sure the screen name is either a human or bot. Create human_player if its someone new.
        :param sn: The screen name e.g. @rawkintrevo (but no '@' so really 'rawkintrevo')
        :return:
        """
        if sn not in self.human_players:
            if sn not in self.bot_players:
                self._add_human_to_chars(sn)
            else:
                print("'%s' exists as bot" % sn)
        else:
            print("'%s' exists as human" %sn)

    def _load_random_name(self):
        """
        Someday this will load a list of TNG characters who don't have bots in descending order of frequency of lines.
        :return:
        """
        """
        These are the characters that can be randomly assigned to a user who 'chimes in', in the future need to up date 
        this to use decreasingly popular characters after the "main characters" (who will have their own bots)
        """
        unused_tng_characters = [ 'BARCLAY',
                                  'CRUSHER',
                                  "LWAXANA",
                                  "Q",
                                  'TASHA',
                                  'WESLEY']

        # randomly assign person to screen name
        name = unused_tng_characters[random.randint(0, len(unused_tng_characters)) -1]
        # keep looking if it's already assigned
        while name in self.human_players:
            name = unused_tng_characters[random.randint(0, len(unused_tng_characters))]
        return name

    def _make_legit_words(self, story):
        """
        Later we'll use this to try capitalizing / un capitalizing words to find ones in the dictionary
        :param story:
        :return:
        """
        words = [w for w in story.split() if w in vocab_in]
        story = " ".join(words[-100:])
        return story

    def _story_post_processing(self, story):
        # ## Clear the Narrartor Bot markups #should be done now by convert_sn_to_script_name
        # do the main chars @s first
        print("message_to_story_postprocessing: %s" % story)
        for k, v in self.at_bot_players.items():
            print("replacing %s with %s" % (k,v))
            story = story.replace(k, v)
        for k, v in self.bot_players.items():
            print("replacing %s with %s" % (k,v))
            story = story.replace(k, v)
        # now do the human chars done earlier
        for k, v in self.human_players.items():
            print("replacing %s with %s" % (k,v))
        story = story.replace("@%s" % k, v)
        # replace all " punc " with "punc "
        for p in string.punctuation:
            story = story.replace(p, " %s " % p)
        story = story.replace("@", "")
        print("story with all words: %s" % story)
        story = self._make_legit_words(story)
        print("story with only legit words: %s" % story)
        return story

    def _replace_screennames_with_script_names(self, tweet):
        if tweet.text is None:
            print("nothing to say...")
            return False
        print("Ensuring '%s' exists as human or bot" % tweet.user.screen_name)
        self._ensure_sn_exists(tweet.user.screen_name)
        sn = self._convert_sn_to_script_name(tweet.user.screen_name)
        print("tweet convereted to story '%s'" % (sn + tweet.text))
        return sn + tweet.text

    ####################################################################################################################
    ### Tweet methods

    def tweet(self, speaker, line, in_reply_to_id):
        if line == "":
            return False
        print("%s attempting to tweet '%s'" % (speaker, line))
        try:
            last_tweet = self.apis[speaker].update_status(line,
                                                          in_reply_to_status_id = in_reply_to_id,
                                                          auto_populate_reply_metadata=True)
        except tweepy.error.TweepError as e:
            print("Error on Tweet:")
            print(e)
            return False
        self.tweets_hx.append(last_tweet)
        print("SUCCESS")
        return True

    def prep_next_line_for_tweeting(self, line):
        print("Cleaning up '%s' " % line)
        ## Clean up punctuation
        for p in string.punctuation:
            line = line.replace(" %s" %p, p)
        if "'" in line:
            line = line.replace("' ", "'")
        ## if the 'sayer' of the tweet has their own bot- let them say it.
        if any([k in line for k in self.apis.keys()]):
            speaker = [k for k in self.apis.keys() if k in line][0]
            print("Found '%s' in line."  % speaker)
            line = line.replace(speaker, "")
            if ":" in line:
                line = line.replace(":", "")
            return speaker, line
        ## elif: the sayer is a human, have PICARD ask them what they think. (and wait for answer)
        elif any([v in line for k, v in self.human_players.items()]):
            speaker = [k for k, v in self.human_players.items() if v in line][0]
            random_emoji_str = "".join([emojis[ random.choice(list(emojis.keys()))] for i in range(5)])
            self._what_do_you_think_tweet(speaker, self.human_players[speaker], random_emoji_str)
            return None, None
        ## else: the narrator says it
        else:
            return "narrator", line

    def _wait_for_human(self):
        """
        This method
        1. checks if last tweet was a "what should we do" tweet
        2. if not counts how long since a human said something
        - if too long will tweet "wswd"
        3. otherwise returns False
        :return: BOOL
        """
        # Check last tweet for 'what should we do?'
        if "What do you think" in self.tweets_hx[-1].text:
            print("Detected 'What do you think' in last text... will wait for human input")
            return True
        # Check index of last human tweet vs current
        if len(self.tweets_hx) ==1:
            # ow there are no humans to wait for and we fail
            return False
        last_human = max([i for i in range(len(self.tweets_hx)) if self.tweets_hx[i].author.screen_name in self.human_players.keys()])
        if last_human < len(self.tweets_hx) - 15:
            print("It has been too long, we will wait for humans now...")
            self._tweet_wait_for_human()
            return True
        return False

    def _tweet_wait_for_human(self):
        humans = list(self.human_players.keys())
        print("detected following humans in this conversation: ", humans)
        human_i = random.randint(0, len(humans) - 1)
        print("attempting to call on human %i" % human_i)
        human = humans[human_i]
        random_emoji_str = "".join([emojis[ random.choice(list(emojis.keys()))] for i in range(5)])
        self._what_do_you_think_tweet(human, self.human_players[human], random_emoji_str)

    def _what_do_you_think_tweet(self, screen_name, script_name, random_str):
        self.tweet("PICARD", "What do you think @%s?? (a.k.a. %s) %s" % (screen_name, script_name, random_str),
                   self.tweets_hx[-1].id)