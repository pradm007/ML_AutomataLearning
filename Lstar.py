from ObservationTable import ObservationTable
# import DFA
from inferrer.automaton import dfa
from time import clock
import inferrer

def run_lstar(teacher,time_limit):
    table = ObservationTable(teacher.alphabet,teacher)
    start = clock()
    teacher.counterexample_generator.set_time_limit(time_limit,start)
    table.set_time_limit(time_limit,start)

    learner = inferrer.Learner(alphabet=set(teacher.alphabet), oracle=inferrer.oracle.PassiveOracle(teacher.starting_example_custom[0],
                                                                                           teacher.starting_example_custom[1])
                            ,teacher=teacher
                           ,algorithm="nlstar", time_limit=time_limit, start = start)

    dfa = learner.learn_grammar()

    return dfa