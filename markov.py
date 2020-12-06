#Importing libraries
from scipy.sparse import dok_matrix 
import random
import numpy as np
import sys

class Markov():
  
  '''
    Markov class for generating random text based on previous n-words. 
    Pre-processing of the text is carried out in __init__ function where special charachters '-','(','—',')' are removed.
    Punctuations which inclde '.',',','!','?' are not removed so as to include it in the generated text. 
    
    After preprocessing a markov model is created based on the inputs recieved by the user.
    
    For e.g. if n = 2 a markov chain of 2 words is created that is all possible bigrams of the corpus 
    is stored in a dictionary and their counts in a transition matrix.
  '''
  
  
  #Preprocessing of the text
  def __init__(self,text):
    self.corpus = text
    self.corpus = self.corpus.replace('“', ' " ')
    self.corpus = self.corpus.replace('”', ' " ')
    
    #Removing unwanted charachters from the text corpus.
  
    for spaced in ['-','(','—',')']:
      self.corpus = self.corpus.replace(spaced, ' '.format(spaced))
      
    #Providing a space between any special charachter so that it can be treated as a unique token
    
    for spaced in ['.',',','!','?']:
      self.corpus = self.corpus.replace(spaced, ' {0} '.format(spaced))

  #Short Summary of the text such as number of unique tokens, total number of tokens
  
  def summary(self,text):
    total_words = text.split(' ')
    total_words= [word for word in total_words if word != '']
    unique_words = list(set(total_words))
    word_index_dict = {word: i for i, word in enumerate(unique_words)}
    unique_words_count = len(list(set(total_words)))
    return total_words,unique_words, word_index_dict
  
  #Summary to print
  
  def show_summary(self):
    total_words,unique_words, word_index_dict = self.summary(self.corpus)
    print("The total number of tokens in the corpus ",len(total_words)) 
    print("The total number of unique tokens in the corpus ",len(unique_words))

#Creating a n-gram markov chain and corresponding transition matrix
  def n_gram(self,n):
    total_words,unique_words,word_index_dict = self.summary(self.corpus)
    #all n-order words are extracted
    sets_of_ngram_words = [ ' '.join(total_words[i:i+n]) for i, _ in enumerate(total_words[:-n]) ]
    sets_count = len(list(set(sets_of_ngram_words)))
    #transition matrix
    next_after_ngram_words_matrix = dok_matrix ((sets_count, len(unique_words)))
    distinct_sets_of_ngram_words = list(set(sets_of_ngram_words))
    ngram_words_idx_dict = {word: i for i, word in enumerate(distinct_sets_of_ngram_words)}
    for i, word in enumerate(sets_of_ngram_words[:-n]):
      word_sequence_idx = ngram_words_idx_dict[word]
      next_word_idx = word_index_dict[total_words[i+n]]
      next_after_ngram_words_matrix[word_sequence_idx, next_word_idx] +=1
    return next_after_ngram_words_matrix , ngram_words_idx_dict

  #a weighted random choice function to select from a given list
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
  
  #Assigning weights to each distinct words to be chosen using weighted_choice function
  def likelihoods(self, word_sequence, next_after_n_words_matrix,n_words_idx_dict, alpha):
    next_word_vector = (next_after_n_words_matrix[n_words_idx_dict[word_sequence]]).toarray() + alpha
    likelihoods = next_word_vector/next_word_vector.sum()
    return likelihoods[0]

  '''
    Function to generate the random sentence with following arguments.
    n: number of previous tokens to consider to build the model
    start: starting sequence to consider
    length: Number of words to generate
    alpha: Hyperparameter
  '''

  def generate(self,n, start, length,alpha):
    next_after_n_words_matrix, n_words_idx_dict = self.n_gram(n)
    if (start in n_words_idx_dict.keys()) == False:
      random_start = np.random.choice(list(n_words_idx_dict.keys()))
      seed = random_start.split(' ')
      sentence = random_start
    else:
      seed = start.split(' ')
      sentence = start
        
      #Iterating over the total length to generate the tokens
      
    for _ in range(length):
      sentence+=' '
      likelihood = self.likelihoods(' '.join(seed), next_after_n_words_matrix,n_words_idx_dict,alpha)
      expected_token = self.ngram_likelihood([likelihood])
      sentence+=expected_token
      seed = seed[1:]+[expected_token]
    return sentence

#Sentences to generate using a combination of 1-word, 2-word, 3-word markov chain
  def mixed_n_generate(self,seed, chain_length,alpha,seed_length=3):
    current_words = seed.split(' ')
    if len(current_words) != seed_length:
        raise ValueError(f'wrong number of words, expected {seed_length}')
    sentence = seed
    next_after_1_words_matrix, n1_words_idx_dict = self.n_gram(1)
    next_after_2_words_matrix, n2_words_idx_dict = self.n_gram(2)
    next_after_3_words_matrix, n3_words_idx_dict = self.n_gram(3)
    for _ in range(chain_length):
        sentence+=' '
        word_sequence1 = current_words[-1:]
        word_sequence2 = current_words[-2:]
        word_sequence3 = current_words[-3:]
        l1 = self.likelihoods(' '.join(word_sequence1), next_after_1_words_matrix,n1_words_idx_dict,alpha)
        if ' '.join(word_sequence2) in [n2_words_idx_dict.keys()]:
          l2 = self.likelihoods(' '.join(word_sequence2), next_after_2_words_matrix,n2_words_idx_dict,alpha)
          if ' '.join(word_sequence3) in [n3_words_idx_dict.keys()]:
            l3 = self.likelihoods(' '.join(word_sequence3), next_after_3_words_matrix,n3_words_idx_dict,alpha)
            l = [l1,l2,l3]
          else:
            l = [l1,l2]
        elif ' '.join(word_sequence3) in [n3_words_idx_dict.keys()]:
          l = [l1,l3]
        else:
          l = [l1]
        next_word = self.ngram_likelihood(l)
        sentence+=next_word
        current_words = current_words+[next_word]
    return sentence

if __name__ == "__main__":
  path = sys.argv[1]
  n = int(sys.argv[2])
  start = sys.argv[3]
  length = int(sys.argv[4])
  alpha = int(sys.argv[5])
  choice = int(sys.argv[6])
  try:
    fileopen = open(path,'r',encoding = 'utf-8')
    text = fileopen.read()
    markov = Markov(text)
    markov.show_summary()
    if choice == 1:
      text = markov.generate(n,start,length,alpha)
      print(markov.generate(n,start,length,alpha))
    elif choice == 2:
      text = markov.mixed_n_generate(start,length,alpha)
      print(text)
    else:
      print("Wrong Choice")
  except:
    print("Path invalid or wrong arguments")
      
