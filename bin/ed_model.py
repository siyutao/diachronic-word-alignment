import editdistance
import numpy as np
import sys, io
from collections import defaultdict

class ED_Model1:

    def __init__(self, d = "data/eval/de-de/de_1781_Rosalino-de_1871_Elberfelder/text", e = "e", f = "f", n = 100000000000, null_padding = False, ed_heuristic = False, ed_decode = False):
        '''
        d - Data filename prefix (default=data)
        e - Suffix of English filename (default=e)
        f - Suffix of French filename (default=f)
        n - Number of sentences to use for training and alignment
        '''
        self.num_sents = n
        self.null_padding = null_padding
        f_data = "%s.%s" % (d, f)
        e_data = "%s.%s" % (d, e)
        self.ed_heuristic = ed_heuristic
        self.ed_decode = ed_decode
        # self.bitext = [[sentence.strip().split() for sentence in pair] for pair in zip(open(f_data), open(e_data))][:self.num_sents]
        self.f_text = [sentence.strip().split() for sentence in open(f_data)][:self.num_sents]
        if self.null_padding:
            self.e_text = [['<NULL>']+sentence.strip().split() for sentence in open(e_data)][:self.num_sents]
        else:
            self.e_text = [sentence.strip().split() for sentence in open(e_data)][:self.num_sents]
        # MOD: get vocab list
        self.f_vocab = list(set([word for sentence in self.f_text for word in sentence]))
        self.e_vocab = list(set([word for sentence in self.e_text for word in sentence]))
        self.f_vocab_size = len(self.f_vocab)
        self.e_vocab_size = len(self.e_vocab)
        self.f_to_index = {}
        self.e_to_index = {}
        for i, f_word in enumerate(self.f_vocab):
            self.f_to_index[f_word] = i
        for j, e_word in enumerate(self.e_vocab):
            self.e_to_index[e_word] = j
        print("f_vocab_size:", self.f_vocab_size)
        print("e_vocab_size:", self.e_vocab_size)
        self.prob = defaultdict(float)

    def gaussian(self, x, mu=0, sig=2):
        return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

    def ed_heuristic_initialization(self, mu=0, sig=2):
        print("Using edit distance for heuristic initialization: (one dot represents 1 percent)")
        ed_array = np.empty(shape=(self.f_vocab_size, self.e_vocab_size))
        LOG_EVERY_N = self.f_vocab_size // 100
        for i, f_word in enumerate(self.f_vocab):
            for j, e_word in enumerate(self.e_vocab):
                ed = editdistance.eval(f_word, e_word)
                ed_array[i,j] = self.gaussian(ed, mu, sig)
            if i % LOG_EVERY_N == 0:
                print('.', end='')
        print()
        # divide each row by its sum
        ed_array = ed_array/ed_array.sum(axis=1, keepdims=True)
        self.heuristic_p = ed_array
        print("Heuristic initialization completed.")
        return None
    
    def em_training(self, num_iter = 5, mu=0, sig=2):
        '''
        function implementing EM algorithm (edited to use numpy array)
        '''
        p = [np.empty(shape=(self.f_vocab_size, self.e_vocab_size))] * (num_iter + 1)
        if self.ed_heuristic:
            self.ed_heuristic_initialization(mu=0, sig=2)
            p[0] = self.heuristic_p
        else:
            p[0] = np.ones(shape=(self.f_vocab_size, self.e_vocab_size))
            p[0] = p[0]/p[0].sum(axis=1, keepdims=True)
        print("EM Training Starting:")
        for k in range(1, num_iter + 1): # iterate for num_iter times
            print('Iteration {0:1}...'.format(k))
            # init all counts to 0.0
            e_count = defaultdict(float)
            fe_count = defaultdict(float)
            # E-Step
            for f, e in zip(self.f_text, self.e_text): # iterate over sentence pairs
                for f_i in f:
                    Z = 0
                    i = self.f_to_index[f_i]
                    for e_j in e:
                        j = self.e_to_index[e_j]
                        Z += p[k-1][i,j]
                    for e_j in e:
                        j = self.e_to_index[e_j]
                        c = p[k-1][i,j] / Z # expected count
                        fe_count[(f_i,e_j)] += c # increase count of alignment
                        e_count[e_j] += c # increase count of English
            # M-Step
            for f, e in fe_count.keys():
                i = self.f_to_index[f]
                j = self.e_to_index[e]
                p[k][i,j] = fe_count[(f,e)]/e_count[e]
        self.prob = p[k]

    def align(self, out = "./output.a", n = 10):
        '''
        align function implementing most probable alignment
        out - output file path
        n - number of sentence pairs to be aligned
        '''
        output = open(out, 'w')
        for f, e in zip(self.f_text[:n], self.e_text[:n]):
            for (i, f_i) in enumerate(f): # for each French word
                best_prob = 0.0
                best_j = 0
                for (j, e_j) in enumerate(e): # iterate through the English words
                    if self.ed_decode:
                        # when using edit distance
                        ed = editdistance.eval(f_i,e_j) + 1
                        index_i = self.f_to_index[f_i]
                        index_j = self.e_to_index[e_j]
                        prob_prime = self.prob[index_i,index_j] / ed
                    else:
                        # default
                        index_i = self.f_to_index[f_i]
                        index_j = self.e_to_index[e_j]
                        prob_prime = self.prob[index_i,index_j]
                    if prob_prime > best_prob:
                        best_prob = prob_prime
                        best_j = j
                if self.null_padding:
                    # using NULL padding
                    if best_j > 0:
                        output.write("%i-%i " % (i,best_j-1))
                else:
                    # default
                    output.write("%i-%i " % (i,best_j))
            output.write("\n")
        output.close()
        print("Aligned {0} sentences.".format(n))
        print("Output to:", out)