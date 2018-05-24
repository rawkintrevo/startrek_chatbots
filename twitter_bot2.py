from time import sleep
from datetime import datetime

import twitter_handler


## Init all conversatoins...
c0 = twitter_handler.Conversation()
# c1 = Conversation()
tweets_to_be_sorted = c0.get_new_tweets()

conv = [c0]
i = 0
# tweet caching prevents rate limit errors
tweet_cache = {t.id_str : t for t in tweets_to_be_sorted}

while len(tweets_to_be_sorted) > 0:
    print("%i: %i tweets remain to be sorted" % (i, len(tweets_to_be_sorted)))
    if i >= len(conv):
        "------------------------------Adding new Conversation()-----------------------------------------------"
        conv.append(twitter_handler.Conversation())
    conv[i].tweet_cache = tweet_cache
    conv[i].find_ids_in_conversation(tweets_to_be_sorted[0])
    tweet_cache.update(conv[i].tweet_cache)
    tweets_to_be_sorted = [m for m in tweets_to_be_sorted if m not in conv[i].tweets_hx]
    i += 1
print("Done sorting tweets into conversations")

# The Role of creates off shoots.
conv = [c for c in conv if "The role of" not in c.tweets_hx[-1].text]

conv = [c for c in conv if c.tweets_hx[-1].created_at > datetime(2018,5,22,17,4)]

print("\n".join(["Conversatoin: %i tweets" % len(c.tweets_hx) for c in conv]))
while True:
    print(datetime.now().strftime("%Y:%m:%d %H:%M:%s"))
    tweets_to_be_sorted = [t for t in c0.get_new_tweets() if t.id_str not in tweet_cache]
    new_conv_tweets = [m for m in tweets_to_be_sorted if m.in_reply_to_status_id is None]
    ## Create New Conversatoins
    for t in new_conv_tweets:
        print("New conversation, opening text: %s" % t.text)
        conv.append(twitter_handler.Conversation())
        conv[-1].tweets_hx.append(t)
        tweet_cache[t.id_str] = t

    ## Check for in_reply_to_status is None, create new conversatoin for those tweets
    for c in conv:
        ## Get all new tweets (in order)
        while True:
            new_tweets = [m for m in tweets_to_be_sorted if m.in_reply_to_status_id == c.tweets_hx[-1].id]
            if len(new_tweets) > 0:
                c.tweets_hx.append(new_tweets[0])
                tweet_cache[t.id_str] = t
            else:
                break
        c.next_tweet()
    sleep(60)
# for tweet in new tweets create a new timeline
# pass

#


    # what should we do tweet

# only tweet if last tweet wasn't a "what should we do" tweet.
