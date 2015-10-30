#!/usr/bin/env python
# coding:utf-8

__author__ = "Chao Chen"
__uni__ = "cc3736"

from copy import deepcopy
import time

ROW = "ABCDEFGHI"
COL = "123456789"
ROW_MAP = {"A": "1",
           "B": "2",
           "C": "3",
           "D": "4",
           "E": "5",
           "F": "6",
           "G": "7",
           "H": "8",
           "I": "9"}
OUTPUT_FILENAME = "output.txt"


# utility function to print each sudoku
def print_sudoku(sudoku):
    print "-----------------"
    for i in ROW:
        for j in COL:
            print sudoku[i + j],
        print ""


# utility function to write the OUTPUT_FILENAME to the file
def write_to_file(sudoku):
    content = "-----------------\n"
    for i in ROW:
        for j in COL:
            content += str(sudoku[i + j]) + " "
        content += "\n"
    try:
        with open(OUTPUT_FILENAME, 'a') as fw:
            fw.write(content)
    except:
        print "Error in writing the OUTPUT_FILENAME file."
        exit()

# Reading of sudoku list from file
try:
    f = open("sudokus.txt", "r")
    sudokuList = f.read()
except:
    print "Error in reading the sudoku file."
    exit()


# class csp is to be instantiated for each case.
# The instance generates and stores detailed information of the game case,
# including the node list/dict(every node's neighbors and domain), arc list,
#  primary sudoku map and solved sudoku map.
class CSP:
    primary_sudoku = {}
    solved_sudoku = {}

    # Store node information in dict structure.(Easy to implement search)
    # Used by AC-3
    # Example:
    # node_dict = {"A1": {"domain":[1,2,3], "neighbors": ["A2", "A3", "B1"]},
    #              "B1": {"domain":[3], "neighbors": ["A1", "B2", "B3"]},
    #              "B2": {"domain":[5,6,8], "neighbors": ["A2", "B1", "B3"]},
    #               ...}
    node_dict = {}

    # Store node information in list structure.(Easy to implement sort)
    # Used by backtracking search
    # Example:
    #   node_list = [["A1", [1,2,3], ["C1","A2"]],
    #                ["B1", [3], ["C1","B2"]],
    #                ["B2", [5,6,8], ["C2","A2"]],
    #                ...]
    node_list = []

    # Directed arcs.
    # Example:
    #   arc_list = [["A1","B1"], //means A1->B1
    #               ["B3","C5"], //means B3->C5
    #              ...]
    arc_list = []

    # utility to initialize a CSP instance
    def __init__(self, one_sudoku=None):
        self.solved_sudoku = {}
        self.node_list = []
        self.node_dict = {}
        self.arc_list = []
        self.primary_sudoku = {}

        if one_sudoku is not None:
            self.primary_sudoku = one_sudoku

            for i in ROW:
                for j in COL:
                    if one_sudoku[i + j] != 0:
                        continue

                    name = i + j
                    domain = range(1, 10, 1)
                    neighbors = []

                    # deal with neighbors in the same column
                    for r in ROW:
                        neighbor_val = one_sudoku[r + j]
                        if neighbor_val == 0 and r != i:
                            neighbors.append(r + j)
                            self.arc_list.append([name, r + j])
                        elif domain.__contains__(neighbor_val):
                            domain.remove(neighbor_val)

                    # deal with neighbors in the same row
                    for c in COL:
                        neighbor_val = one_sudoku[i + c]
                        if neighbor_val == 0 and c != j:
                            neighbors.append(i + c)
                            self.arc_list.append([name, i + c])
                        elif domain.__contains__(neighbor_val):
                            domain.remove(neighbor_val)

                    # deal with the neighbors in the same block
                    # block is defined as [m,n]
                    #   [0,0] [0,1] [0,2]
                    #   [1,0] [1,1] [1,2]
                    #   [2,0] [2,1] [2,2]

                    m = (int(ROW_MAP[i]) - 1) / 3
                    n = (int(j) - 1) / 3

                    for p in xrange(3):
                        for q in xrange(3):
                            n1 = ROW[m * 3 + p]
                            n2 = COL[n * 3 + q]
                            neighbor_val = one_sudoku[n1 + n2]
                            if neighbor_val == 0 and not (n1 == i or n2 == j):
                                neighbors.append(n1 + n2)
                                self.arc_list.append([name, n1 + n2])
                            elif domain.__contains__(neighbor_val):
                                domain.remove(neighbor_val)

                    self.node_list.append([name, domain, neighbors])
                    self.node_dict[name] = {"domain": domain, "neighbors": neighbors}

    # utility used for AC-3 to check whether all variables are reduced to one value.
    def solved(self):
        for i in ROW:
            for j in COL:
                if self.node_dict.__contains__(i + j) and self.node_dict.get(i + j).get("domain").__len__() != 1:
                    return False
        return True

    # utility used by backtracking search to merge the assignment into the sudoku map.
    def update(self, assignment):
        for i in ROW:
            for j in COL:
                if self.primary_sudoku[i + j] != 0:
                    self.solved_sudoku[i + j] = self.primary_sudoku[i + j]
                else:
                    self.solved_sudoku[i + j] = assignment[i + j]


def remove_inconsistent_values(arc, node_dict):
    x1 = arc[0]
    x2 = arc[1]
    removed = False
    for x in node_dict[x1]["domain"]:
        y_domain = node_dict[x2]["domain"]
        if y_domain == [x]:
            node_dict[x1]["domain"].remove(x)
            removed = True
    return removed


def ac_3(csp):
    node_dict = csp.node_dict
    queue = deepcopy(csp.arc_list)
    while queue.__len__() != 0:
        arc = queue.pop(0)
        if remove_inconsistent_values(arc, node_dict):
            for neighbor in node_dict[arc[0]]["neighbors"]:
                if not queue.__contains__([neighbor, arc[0]]):
                    queue.append([neighbor, arc[0]])
    return csp


# sort key
# sorted by number of values in the domain
def f(x):
    return x[1].__len__()


# sort key
def g(x):
    return x[1]


def index(unassigned_list, var):
    for i in xrange(unassigned_list.__len__()):
        if unassigned_list[i][0] == var:
            return i
    return -1


# utility used by backtracking search
# to pick out an unassigned node from the list.
# The node with smallest size of domain will be picked out.
def select_unassigned_variable(assignment, unassigned_list, csp):
    unassigned_list.sort(key=f)
    return unassigned_list[0][0]


# utility used by backtracking search
# to get a ordered domain of the node based on some ordering strategy.
# Least constraining value will be put in the first place of the list
def order_domain_values(var, assignment, unassigned_list, csp):
    domain_list = unassigned_list[index(unassigned_list, var)][1]
    domain_list_extend = []
    for candidate_value in domain_list:
        count = 0
        for neighbor in csp.node_dict[var]["neighbors"]:
            i = index(unassigned_list, neighbor)
            if i != -1:
                if unassigned_list[i][1].__contains__(candidate_value):
                    count += 1
        domain_list_extend.append([candidate_value, count])
    domain_list_extend.sort(key=g)
    domain_list = []
    for pair in domain_list_extend:
        domain_list.append(pair[0])
    return domain_list


# utility used by backtracking search
# to decide whether the value to be assigned will conflict with some node that has already been assigned.
# @return True if it's consistent;
#         False if there are some conflicts.
def is_consistent(var, value, assignment, csp):
    for neighbor in csp.node_dict[var]["neighbors"]:
        if assignment.__contains__(neighbor) and assignment[neighbor] == value:
            return False
    return True


# utility used by backtracking search
# to forward check and update the unassigned list
# if some of it's neighbors are not assigned yet, their domain will be checked.
# The to-assigned value will be deleted from these neighbors' domain.
# @return True if no conflict exists.
#         False if some node has no candidate in it's domain after the deletion.
def forward_checking(var, value, unassigned_list, csp):
    for neighbor in csp.node_dict[var]["neighbors"]:
        i = index(unassigned_list, neighbor)
        if i != -1:
            if unassigned_list[i][1].__contains__(value):
                unassigned_list[i][1].remove(value)

                if unassigned_list[i][1].__len__() == 0:
                    return False
    return True


def recursive_backtracking(assignment, unassigned_list, csp):
    # if all nodes are assigned, return the assignment
    if assignment.__len__() == csp.node_list.__len__():
        return assignment

    var = select_unassigned_variable(assignment, unassigned_list, csp)
    for value in order_domain_values(var, assignment, unassigned_list, csp):
        if is_consistent(var, value, assignment, csp):
            assignment[var] = value
            unassigned_list_backup = deepcopy(unassigned_list)  #backup the unassigned list to be potentially recovered later.

            unassigned_list.__delitem__(index(unassigned_list, var))

            if forward_checking(var, value, unassigned_list, csp) is False:
                result = False
            else:
                result = recursive_backtracking(assignment, unassigned_list, csp)
            if result is not False:
                return result
            assignment.__delitem__(var)
            unassigned_list = unassigned_list_backup

    return False


def backtracking_search(csp):
    return recursive_backtracking({}, deepcopy(csp.node_list), csp)

st = time.time()
# 1.5 count_correct_solution number of sudokus solved by AC-3
num_ac3_solved = 0
for line in sudokuList.split("\n"):
    # Parse sudokuList to individual sudoku in dict, e.g. sudoku["A2"] = 1
    sudoku = {ROW[i] + COL[j]: int(line[9 * i + j]) for i in range(9) for j in range(9)}
    csp = CSP(sudoku)
    csp = ac_3(csp)
    '''
    for var in csp.node_list:
        node = csp.node_dict[var[0]]
        print var[0], ":", node["domain"], " ",
    print ""
    '''

    if csp.solved():
        num_ac3_solved += 1
print "Number of sudokus solved by AC-3: ", num_ac3_solved
en = time.time()
print en-st


a = time.time()
# create output file
try:
    open(OUTPUT_FILENAME, 'wt').close()
except:
    print "Error in creating OUTPUT_FILENAME.txt"
    exit()

# 1.6 solve all sudokus by backtracking
num_backtracking_search_solved = 0
for line in sudokuList.split("\n"):
    # Parse sudokuList to individual sudoku in dict, e.g. sudoku["A2"] = 1
    sudoku = {ROW[i] + COL[j]: int(line[9 * i + j]) for i in range(9) for j in range(9)}
    csp = CSP(sudoku)
    solution = backtracking_search(csp)
    if solution is not False:
        num_backtracking_search_solved += 1
        csp.update(solution)
        print_sudoku(csp.solved_sudoku)
        write_to_file(csp.solved_sudoku)
b = time.time()
print "Number of sudokus solved by Back-Tracking Search: ", num_backtracking_search_solved
print "Total Running time by Backtracking Search (s): ", b-a
print "\n\n####################################"
print "Total statistics:"
print "AC-3 solved: ", num_ac3_solved
print "Backtracking-Search solved: ", num_backtracking_search_solved
print "####################################"





