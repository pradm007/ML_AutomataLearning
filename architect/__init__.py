import os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))


from architect.architect import Learner
from architect import utils
from architect import automaton
from architect import algorithms
from architect import oracle
