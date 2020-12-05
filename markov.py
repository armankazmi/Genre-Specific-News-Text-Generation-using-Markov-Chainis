from scipy.sparse import dok_matrix 
import random
import numpy as np

class Markov():
  def __init__(self,text):
    self.corpus = text
    self.corpus = self.corpus.replace('“', ' " ')
    self.corpus = self.corpus.replace('”', ' " ')
    for spaced in ['-','(','—',')']:
      self.corpus = self.corpus.replace(spaced, ' '.format(spaced))
    for spaced in ['.',',','!','?']:
      self.corpus = self.corpus.replace(spaced, ' {0} '.format(spaced))

  def summary(self,text):
    total_words = text.split(' ')
    total_words= [word for word in total_words if word != '']
    unique_words = list(set(total_words))
    word_index_dict = {word: i for i, word in enumerate(unique_words)}
    unique_words_count = len(list(set(total_words)))
    return total_words,unique_words, word_index_dict
  
  def show_summary(self):
    total_words,unique_words, word_index_dict = self.summary(self.corpus)
    print("The total number of tokens in the corpus ",len(total_words))
    print("The total number of unique tokens in the corpus ",len(unique_words))


  def n_gram(self,n):
    total_words,unique_words,word_index_dict = self.summary(self.corpus)
    sets_of_ngram_words = [ ' '.join(total_words[i:i+n]) for i, _ in enumerate(total_words[:-n]) ]
    sets_count = len(list(set(sets_of_ngram_words)))
    next_after_ngram_words_matrix = dok_matrix ((sets_count, len(unique_words)))
    distinct_sets_of_ngram_words = list(set(sets_of_ngram_words))
    ngram_words_idx_dict = {word: i for i, word in enumerate(distinct_sets_of_ngram_words)}
    for i, word in enumerate(sets_of_ngram_words[:-n]):
      word_sequence_idx = ngram_words_idx_dict[word]
      next_word_idx = word_index_dict[total_words[i+n]]
      next_after_ngram_words_matrix[word_sequence_idx, next_word_idx] +=1
    return next_after_ngram_words_matrix , ngram_words_idx_dict

  def weighted_choice(self,choices, weights):
    total = sum(weights)
    treshold = random.uniform(0, total)
    for k, weight in enumerate(weights):
        total -= weight
        if total < treshold:
            return choices[k]
  
  def ngram_likelihood(self,likelihood_list):
    l_max = []
    for i in range(len(likelihood_list)):
      l_max.append(likelihood_list[i].max())
    # sample = [l1,l2,l3]
    idx = l_max.index(max(l_max))
    total_words,unique_words,word_index_dict = self.summary(self.corpus)
    return self.weighted_choice(unique_words, likelihood_list[idx])
  
  
  def likelihoods(self, word_sequence, next_after_n_words_matrix,n_words_idx_dict, alpha):
      next_word_vector = (next_after_n_words_matrix[n_words_idx_dict[word_sequence]]).toarray() + alpha
      likelihoods = next_word_vector/next_word_vector.sum()
      return likelihoods[0]

  def generate(self,n, start, length,alpha):
      seed = start.split(' ')
      if len(seed) != n:
          raise ValueError(f'wrong number of words, expected {n}')
      sentence = start
      next_after_n_words_matrix, n_words_idx_dict = self.n_gram(n)
      for _ in range(length):
          sentence+=' '
          likelihood = self.likelihoods(' '.join(seed), next_after_n_words_matrix,n_words_idx_dict,alpha)
          expected_token = self.ngram_likelihood([likelihood])
          sentence+=expected_token
          seed = seed[1:]+[expected_token]
      return sentence
