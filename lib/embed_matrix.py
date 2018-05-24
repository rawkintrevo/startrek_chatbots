

import os
import string

from gensim.models.keyedvectors import KeyedVectors
import numpy as np


def getWordEmbeddingsMatrix(script_directory, embedding_file):
    """
    PAD and EOS are zero vector
    UNK is ones vector
    :param script_directory:
    :param embedding_file:
    :return:
    """
    translator = str.maketrans('', '', string.punctuation)
    all_words = []
    print("Loading vocab from text files in:")
    for d in os.listdir(script_directory):
        print(d)
        for fname in os.listdir("%s/%s" % (script_directory, d)):
            with open("%s/%s/%s" % (script_directory, d, fname), 'r') as f:
                words = [w.translate(translator) for w in f.read().split() if w.translate(translator) != ""]
            all_words.extend(words)

    model = KeyedVectors.load_word2vec_format(embedding_file, binary=True)
    vocab = {"PAD" : 0, "EOS" : 1}
    vocab.update({w : i + 2 for i,w in enumerate([w1 for w1 in set(all_words) if w1 in model]) })
    inv_dict = vocab.keys()
    ## Take a minute to load...

    vocab_size = len(inv_dict)
    emb_size = 300 # or whatever the size of your embeddings
    embeddings = np.zeros((vocab_size + 1, emb_size))
    for k,v in vocab.items():
        embeddings[v] = model[k]
    vocab["UNK"] = len(vocab.keys())
    embeddings[vocab["UNK"]] = np.ones(emb_size)
    del model
    ## Now we have a numpy matrix of embeddings...
    # x_model = tf.placeholder(tf.int32, shape=[None, input_size])
    # with tf.device("/cpu:0"):
    #     embedded_x = tf.nn.embedding_lookup(embeddings, x_model)
    return embeddings, vocab