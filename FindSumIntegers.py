from dwave.system import EmbeddingComposite, DWaveSampler
from dimod import BinaryQuadraticModel
from collections import defaultdict
import neal
import sys


# generate an ordered and evenly spaced list of the given size
def get_list(size):
    S = [i + 1 for i in range(size)]
    return S


# generates the variables
def gen_var(num):
    return f"{num}"


# generate the QUBO and fill in the matrix. This is based on the QUBO equation I formulated
def gen_QUBO(S, N, C, gamma):
    Q = defaultdict(int)  # create a QUBO matrix
    offset = N ** 2 + (C ** 2 * gamma)  # calculate the offset or constant of the QUBO equation

    # objective function
    for i in range(len(S)):
        var_i = gen_var(S[i])
        Q[(var_i, var_i)] += S[i] * S[i] - 2 * N * S[i]  # fill in the linear diagonal terms on our QUBO matrix
        for j in range(i + 1, len(S)):
            var_j = gen_var(S[j])
            Q[(var_i, var_j)] += 2 * S[i] * S[j]  # fill in the quadratic off-diagonal terms on our QUBO matrix

    # constraint function
    for i in range(len(S)):
        var_i = gen_var(S[i])
        Q[(var_i, var_i)] += (1 - 2 * C) * gamma  # fill in the linear diagonal terms
        for j in range(i + 1, len(S)):
            var_j = gen_var(S[j])
            Q[(var_i, var_j)] += 2 * gamma  # fill in the quadratic off-diagonal terms

    return Q, offset  # return the QUBO matrix and the offset


# solve the QUBO and return the sample set
def solve_QUBO(Q, o):
    bqm = BinaryQuadraticModel.from_qubo(Q, offset=o)  # conversion of QUBO to BQM
    sampler = neal.SimulatedAnnealingSampler()  # selecting the sampler
    return sampler.sample(bqm, num_reads=200)  # generating and returning the sampleset


# print the best solution found by the annealer
def print_result(sample):
    print()
    solution = []  # the numbers forming part of our solution will be stored here
    # checking to see which numbers are in our solution
    for var, val in sample.items():
        if val == 1:  # this is the value of the qubit. If it is one, then its associated number forms part of solution
            solution.append(int(var))
    solution.sort()
    # printing out the numbers in the solution
    for i in solution:
        sys.stdout.write(str(i) + "\t")
    print()

    return solution  # returning the solution list of numbers


# used for checking the solution list of numbers
def check_result(solution, N, C):
    # we need the numbers in the list of numbers to sum up to N and we need C numbers in the list for the correct soln
    if N == sum(solution) and len(solution) == C:
        return 'These {} numbers sum to '.format(len(solution)) + str(sum(solution)) + " : " + 'correct solution'
    else:
        return 'These {} numbers sum to '.format(len(solution)) + str(sum(solution)) + " : " + 'incorrect solution'


def main():
    S = get_list(250)  # generate list by specifying the size
    N = 1156  # THis is the number we want a set of numbers to sum up to
    C = 23  # this is the number of numbers that should be used in our solution
    gamma = 5000  # we may need to increase this is if the obj-
    # ective function is too dominant and the constraint is not satisfied
    Q, offset = gen_QUBO(S, N, C, gamma)  # generate the QUBO and offset and store the results
    sampleset = solve_QUBO(Q, offset)  # obtain the sampleset
    print(sampleset)  # print the sampleset
    solution = print_result(sampleset.first.sample)  # print the best solution found
    print(check_result(solution, N, C))  # check if the best solution is correct


if __name__ == '__main__':
    main()
