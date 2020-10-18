from observationtable.ObservationTable import ObservationTable
import architect
from time import clock
from neuralnets.Teacher import Teacher

# def dfa_maker(teacher,time_limit):
def dfa_maker(rnn,time_limit = 50,initial_split_depth = 10,starting_examples=None, algorithm=str):

    print("Starting examples :", starting_examples)
    guided_teacher = Teacher(rnn, num_dims_initial_split=initial_split_depth, starting_examples=starting_examples)
    table = ObservationTable(rnn.alphabet,guided_teacher)

    start = clock()
    guided_teacher.counterexample_generator.set_time_limit(time_limit,start)
    table.set_time_limit(time_limit,start)

    learner = architect.Learner(alphabet=set(guided_teacher.alphabet),
                                # oracle=architect.oracle.ActiveOracle(None),
                                oracle=architect.oracle.PassiveOracle(starting_examples[0], starting_examples[1]),
                                teacher=guided_teacher,
                                algorithm=algorithm,
                                time_limit=time_limit,
                                start = start)

    dfa = learner.learn_grammar()

    end = clock()
    extraction_time = end - start

    dfa = guided_teacher.dfas[-1]

    print("Extraction time : " + str(extraction_time))
    # print("Counter examples generated were: (format: (counterexample, counterexample generation time))")
    # print('\n'.join([str(a) for a in guided_teacher.counterexamples_with_times]))

    return dfa