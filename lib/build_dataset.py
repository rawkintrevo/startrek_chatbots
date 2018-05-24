

import numpy as np
import os
import string

from random import randint

from lib.embed_matrix import getWordEmbeddingsMatrix

class DataGenerator():

    def __init__(self, embedding_file, script_directory):
        self.script_directory = script_directory
        self.embeddingsMatrix, self.vocab = getWordEmbeddingsMatrix(self.script_directory, embedding_file)
        self.all_words = list()
        self.load_all_words()


    def get_next_eos(self, all_words, start_i= 0):
        start_i += 1
        last_word_was_eos = False
        while True:
            current_word_is_eos = all_words[start_i] == 'EOS'
            if last_word_was_eos == True and current_word_is_eos == False:
                break
            if current_word_is_eos:
                last_word_was_eos = True
            start_i += 1
        return start_i


    def load_all_words(self):
        translator = str.maketrans('', '', string.punctuation)
        all_words = []
        print("Loading vocab from text files in:")
        for d in os.listdir(self.script_directory):
            print(d)
            for fname in os.listdir("%s/%s" % (self.script_directory, d)):
                with open("%s/%s/%s" % (self.script_directory, d, fname), 'r') as f:
                    words = f.read().replace(".", " EOS ").split()
                    words = [w.translate(translator) for w in words if w.translate(translator) != ""]
                all_words.extend(words)
        for i in range(len(all_words)):
            if all_words[i] in self.vocab:
                continue
            else:
                all_words[i] = 'UNK'
        self.all_words = all_words


    def get_next_batch(self, num_samples_in_batch, seq_length, word_dim = 300):
        decoder_inputs = np.zeros((num_samples_in_batch, seq_length, word_dim))
        encoder_inputs = np.zeros((num_samples_in_batch, seq_length, word_dim))
        target_outputs =  np.zeros((num_samples_in_batch, seq_length, word_dim))
        for i in range(num_samples_in_batch):
            start_i = randint(0, len(self.all_words))
            start_i = self.get_next_eos(self.all_words, start_i)
            targt_i = self.get_next_eos(self.all_words, start_i)
            input_seq_words = self.all_words[start_i:start_i + seq_length]
            target_seq_words = self.all_words[targt_i:targt_i + seq_length]
            for j in range(len(input_seq_words)):
                if input_seq_words[j] == "EOS": break
                encoder_inputs[i,seq_length - j] = self.embeddingsMatrix[self.vocab[input_seq_words[j]]] # encoder inputs are reverse ordered
            for j in range(len(target_seq_words)):
                if target_seq_words[j] == "EOS": break
                decoder_inputs[i,j] = self.embeddingsMatrix[self.vocab[target_seq_words[j]]]
                target_outputs[i,j + 1] = self.embeddingsMatrix[self.vocab[target_seq_words[j]]] # target_outputs are one time step further along
        return encoder_inputs, decoder_inputs, target_outputs

    def get_next(self, num_samples_in_batch, seq_length, word_dim = 300):
        decoder_inputs = np.zeros((num_samples_in_batch, seq_length))
        encoder_inputs = np.zeros((num_samples_in_batch, seq_length))
        target_outputs =  np.zeros((num_samples_in_batch, seq_length))
        for i in range(num_samples_in_batch):
            start_i = randint(0, len(self.all_words))
            start_i = self.get_next_eos(self.all_words, start_i)
            targt_i = self.get_next_eos(self.all_words, start_i)
            input_seq_words = self.all_words[start_i:start_i + seq_length]
            target_seq_words = self.all_words[targt_i:targt_i + seq_length]
            for j in range(len(input_seq_words)):
                if input_seq_words[j] == "EOS": break
                encoder_inputs[i,seq_length - j] = self.vocab[input_seq_words[j]] # encoder inputs are reverse ordered
            for j in range(len(target_seq_words)):
                if target_seq_words[j] == "EOS": break
                decoder_inputs[i,j] = self.vocab[target_seq_words[j]]
                target_outputs[i,j + 1] = self.vocab[target_seq_words[j]] # target_outputs are one time step further along
        return encoder_inputs, decoder_inputs, target_outputs