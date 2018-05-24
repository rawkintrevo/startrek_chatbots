
# Rules for Star Trek Bots

1. StarTrek Bots were trained using [Google's NMT](https://github.com/tensorflow/nmt) (uses Tensorflow).

2. The model is trained on StarTrek scripts which you can find at [http://www.chakoteya.net/StarTrek/index.html](http://www.chakoteya.net)

3. Tweet at one of the current bots (if the system is online) this will kick off a new "episode".  The bots will reply in a conversation.

4. The narrator will assign you as a StarTrek TNG character who isn't already being played by a bot. 

5. The model will reconstruct the conversation and feed it into the NMT model (the last 100 words). 

6. If the next line should be said by a character a human has been assigned, BotPicard will ask "What do you think? <emojis>"

7. The emojis are there because Picard says that a lot, and we need some sort of random string or Twitter will give a duplicate status error.

8. If no human has spoken in the last 15 tweets, Picard will also ask a random human player in the conversation what they think. 
This prevents run-away conversations.  

9. The conversation always halts when a human is asked what they think.

10. Just because Picard asks a certain human what they think, that doesn't mean that human has to respond- any human can respond,
the system will update accordingly. 

11. These are generative chatbots. That is to say, there is no bag of responses, responses are created on the fly by NMT. 

12. If a character is supposed to say something but there is no human or bot player, the narrator will speak for them and add
`NAME_IN_CAPS:` to indicate who said it. 

13. Sometimes you will see things in `[ ]` or `( )`.  In the original scripts, actions are contained in `( )` and new locations
are contained in `[ ]`. For example:

- *RikerBot* : Captain may I speak with you privately? (He grabs his phaser)[Ready Room]

- In this example, after Riker says his line, he grabs his phaser. The scene is now in the Ready Room.

14. The exception to this rule are things like `[On Monitor]`, `[On Viewscreen]` or `[ OC ]` which indicate the person speaking is
on the monitor, on the viewscreen or "On Call" (e.g. on the intercom) respectively.

15. The bots check for responses and generate new respones once per minute. Your response will only "count" if it is the last one in the thread. That means when you see a response you need to reply quickly. 

#### Current Bots

- [Picard](https://twitter.com/BotPicard)
- [Troi](https://twitter.com/BotTroi)
- [LaForge](https://twitter.com/BotLaforge)
- [Riker](https://twitter.com/BotRiker)
- [Worf](https://twitter.com/BotWorf)
- [Data](https://twitter.com/CmdrDataBot)
- [The Narrator](https://twitter.com/ST_NarratorBot)


# Other Dev Notes

#### Importing TF in Python Console for Intellij

Open File > Settings > Build Execution & Deployment > Console > Python

Add LD_LIBRARY_PATH as env variable (with setting to /usr/local/cuda, etc)
