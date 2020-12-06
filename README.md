# News-Text-Generation-using-Markov-Chains

## **Sample**

```f = open("path to corpus")```

```text_corpus = f.read()```

```markov_model = Markov(text_corpus)```

```markov_model.show_summary()```

```markov_model.generate(n,start,length,alpha)```

**n: - previous n words to consider**

**start:- seed words to generate the text**

**length:- number of words to generate in the text**

**alpha :- Hyperparameter, perferably 0 for better results**
