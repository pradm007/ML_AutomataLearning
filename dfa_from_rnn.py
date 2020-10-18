# -*- coding: utf-8 -*-
"""dfa_from_rnn.ipynb

Automatically generated by Colaboratory.

"""

!pip install dynet
!pip install graphviz
!apt-get install graphviz
!git clone -b dev https://github.com/pradm007/ML_AutomataLearning.git
!cp ML_AutomataLearning/*.py .

"""# RNN extraction

### Welcome!

Given a network `rnn` with this API, a DFA can be extracted using `extract(rnn)`. `extract` also has the optional parameters `time_limit` (default: 50 seconds) and `initial_split_depth` (default: 10).

# Code starts here!

### 1. Imports

Implementations of LSTM and GRU classifiers, the Tomita grammars, and our main extraction method.
"""

from neuralnets.LSTM import LSTMNetwork
from neuralnets.RNNClassifier import RNNClassifier
from neuralnets.Training_Functions import make_train_set_for_target,mixed_curriculum_train
from dfa_builder import dfa_maker

"""### 2. Training

#### 2.1. Define a Language
Define a target language for your network. As an example, we have defined the language of all words beginning and ending with the same character, over the alphabet $\{a,b,c\}$.

A language is defined as a function that takes a word over a fixed alphabet and either accepts or rejects it.

You can also pick any one of the seven Tomita grammars we have imported, they are defined over the alphabet $\{0,1\}$. For instance, to use the third Tomita grammar run:
```
target = tomita_3
alphabet = "01"
```
"""

def target(w):
  if len(w)==0:
    return True
  return w[0]==w[-1]
alphabet = "abc"

"""#### 2.2. Create a Train Set
`make_train_set_for_target` returns for the target function a dictionary of words of different lengths, each mapped to its classification by the target. It tries to return a train set with an even split between positive and negative samples for each sample length. Its optional parameters are:
>1. `max_train_samples_per_length` (default 300): the maximum number of words of each length in the train set
>2. `search_size_per_length` (default 1000): the maximum number of words to be sampled from each length while generating the train set
>3. `provided_examples` (default `None`): hand-crafted samples to add to the train set (helpful if random sampling is unlikely to find one of the classes)
>4. `lengths` (a list of integers, default $0-15,20,25,30$): the lengths that will appear in the train set

If the target is such that the positive or negative class is relatively rare, `make_train_set_for_target` is unlikely to create an evenly split test set without some help. In this case it is best to help it with some provided examples, e.g.: for the language of all words containing the sequence `0123` over the alphabet $\{0,1,2,3\}$, you may want to run:
```
short_strings = ["","0","1","2","3"]
positive_examples = [a+"0123"+b for a,b in itertools.product(short_strings,short_strings)]
make_train_set_for_target(target,alphabet,provided_examples=positive_examples)
```
"""

train_set = make_train_set_for_target(target,alphabet)

print(len(train_set))
print(sorted(list(train_set.items()),key=lambda x:len(x[0]))[:6])

"""#### 2.3. Create and Train a Network

`RNNClassifier` generates an RNN-Classifier for a given alphabet.
Its optional parameters are:
>1. `num_layers` (default value 2): the number of hidden layers
>2. `hidden_dim` (default value 5): the size of the hidden layers
>3. `input_dim` (default value 3): the size of the input vectors (these networks use embedding, not one-hot encoding)
>4. `RNNClass` (default value `LSTMNetwork`): the RNN architecture (possible values `LSTMNetwork`, `GRUNetwork`)
"""

rnn = RNNClassifier(alphabet,num_layers=1,hidden_dim=10,RNNClass = LSTMNetwork)

"""The function `mixed_curriculum_train(rnn,train_set)` trains the network `rnn` with the given dictionary of labeled examples, `train_set`. Its optional parameters are: 
>1. `stop_threshold` (default $0.001$): the threshold for the average loss of the network on the train set under which training is cut short
>2. `learning_rate` (defualt 0.001): learning rate for optimiser
>2. `length_epochs` (default $5$): explained below
>3. `random_batch_epochs` (default $100$): below
>4. `random_batch_size` (default $20$): below
>5. `single_batch_epochs` (default $100$): below
>6. `outer_loops` (default $3$): below

`mixed_curriculum_train` splits the input dictionary first into batches by length, training for `length_epochs` iterations each of these batches, by order of increasing length. Then for `random_batch_epochs` iterations it will, at each iteration, split the dictionary into random batches of size `random_batch_size` and train each batch for one iteration. After that it will train the dictionary as one big batch for `single_batch_epochs` iterations. It does all of this `outer_loops` times.

This will print some scatter plots of the average loss on the train set. The plots will come in pairs: each time one for the most recent iterations of training where the whole dictionary was trained as one batch, and another for all the iterations the rnn has been trained since its initialisation.

`mixed_curriculum_train` should work for most simple targets without any tinkering. If the network doesn't drop under the stop threshold, you may want to call it again.
"""

mixed_curriculum_train(rnn,train_set,stop_threshold = 1.5005)

"""### 3. Extraction

#### 3.1. Initial Examples

In Section 7.3 of the paper we note that the process sometimes needs one positive and one negative initial sample to get started. We take these from the training set, using the shortest sample from each class.

If extracting from a network you no longer have the train set for, you can also make such a list manually. 
Of course, there is nothing to stop you from having more than one initial sample from each class, or not using any, and so on.
"""

all_words = sorted(list(train_set.keys()),key=lambda x:len(x))
pos = next((w for w in all_words if rnn.classify_word(w)==True),None)
neg = next((w for w in all_words if rnn.classify_word(w)==False),None)
starting_examples = [w for w in [pos,neg] if not None == w]
print(starting_examples)

"""#### 3.2. Clear the Computation Graph
If you're using our network classes, and just running one network at a time, you don't need this. Still, it's good practice. `renew` function resets the DyNet computation graph and refreshes the calling network's initial vectors.
"""

rnn.renew()

"""#### 3.3. Algorithm
Choose algorithm for abstractions:
supported [ 'lstar', 'nlstar' ]
"""
algorithm = "nlstar"

"""#### 3.4. Extract
It is generally necessary to give the extraction some `starting_examples` to work with, so it doesn't get stuck on a single state automaton (Section 7.3. in the paper). We made those in Section 3.1. of this notebook.

You can set a `time_limit` on the extraction (default $50$ seconds) and the `initial_split_depth` (default $10$) for the initial aggressive refinement (which is described in Section 7.3.1. of our extraction paper).


During extraction, the method will report the counterexamples it finds, how long it took to find each one, and how long it took to refine the observation table (i.e. how long it took to update the $L^*$ automaton) between each two equivalence queries. Every time it starts a new equivalence query, if the proposed DFA has less than $30$ states, it will also display it.
"""

dfa = dfa_maker(rnn, time_limit=10, initial_split_depth= 10, starting_examples=starting_examples, algorithm=algorithm)

"""#### 3.5. Get stats
Display the extracted DFA by using the `draw_nicely` function, which has optional parameters `maximum` (default $60$) and `force` (default `False`), and will only draw the DFA if it has less than `maximum` states or `force` is set to `True`.

Print some statistics you might find interesting about the network, such as the trained RNN's accuracy against its target, the extracted DFA's accuracy against the RNN, and the extracted DFA's accuracy against the original RNN's target.
"""

from math import pow
def percent(num,digits=2):
    tens = pow(10,digits)
    return str(int(100*num*tens)/tens)+"%"

# dfa.draw_nicely(maximum=30) #max size willing to draw

print(dfa.to_regex())
dfa.show()

# if args.show_dfa:
#     dfa.show()

test_set = train_set
print("testing on train set, i.e. test set is train set")
# we're printing stats on the train set for now, but you can define other test sets by using
# make_train_set_for_target

n = len(test_set)
print("test set size:", n)
pos = len([w for w in test_set if target(w)])
print("of which positive:",pos,"("+percent(pos/n)+")")
rnn_target = len([w for w in test_set if rnn.classify_word(w)==target(w)])
print("rnn score against target on test set:",rnn_target,"("+percent(rnn_target/n)+")")
dfa_rnn = len([w for w in test_set if rnn.classify_word(w)==dfa.classify_word(w)])
print("extracted dfa score against rnn on test set:",dfa_rnn,"("+percent(dfa_rnn/n)+")")
dfa_target = len([w for w in test_set if dfa.classify_word(w)==target(w)])
print("extracted dfa score against target on rnn's test set:",dfa_target,"("+percent(dfa_target/n)+")")

