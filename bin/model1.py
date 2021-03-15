import numpy as np
import sys, io
from collections import defaultdict

class Model1:

    def __init__(self, d = "data/eval/de-de/de_1781_Rosalino-de_1871_Elberfelder/text", e = "e", f = "f", n = 100000000000, null_padding = False):
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
        # self.bitext = [[sentence.strip().split() for sentence in pair] for pair in zip(open(f_data), open(e_data))][:self.num_sents]
        self.f_text = [sentence.strip().split() for sentence in open(f_data)][:self.num_sents]
        if self.null_padding:
            self.e_text = [['<NULL>']+sentence.strip().split() for sentence in open(e_data)][:self.num_sents]
        else:
            self.e_text = [sentence.strip().split() for sentence in open(e_data)][:self.num_sents]
        self.f_vocab_size = len(set([word for sentence in self.f_text for word in sentence]))
        self.e_vocab_size = len(set([word for sentence in self.e_text for word in sentence]))
        print("f_vocab_size:", self.f_vocab_size)
        print("e_vocab_size:", self.e_vocab_size)
        self.prob = defaultdict(float)

    def em_training(self, num_iter = 5):
        '''
        function implementing EM algorithm
        num_iter - number of EM iterations (default=5)
        Reference: p.6 Adam Lopez, "Word Alignment and the Expectation-Maximization Algorithm"
        '''
        
        p = defaultdict(lambda: defaultdict(float))

        # initialize theta[0] uniformly, i.e. p(f|e): p[0][(f,e)]= 1/f_vocab
        p[0] = defaultdict(lambda: 1/self.f_vocab_size)

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
                    for e_j in e:
                        Z += p[k-1][(f_i,e_j)]
                    for e_j in e:
                        c = p[k-1][(f_i,e_j)] / Z # expected count
                        fe_count[(f_i,e_j)] += c # increase count of alignment
                        e_count[e_j] += c # increase count of English
            # M-Step
            for f, e in fe_count.keys():
                p[k][(f,e)] = fe_count[(f,e)]/e_count[e]
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
                    if self.prob[(f_i,e_j)] > best_prob:
                        best_prob = self.prob[(f_i,e_j)]
                        best_j = j 
                if self.null_padding:
                    if best_j > 0:
                        output.write("%i-%i " % (i,best_j-1))
                else:
                    output.write("%i-%i " % (i,best_j))
            output.write("\n")
        output.close()
        print("Aligned {0} sentences.".format(n))
        print("Output to:", out)