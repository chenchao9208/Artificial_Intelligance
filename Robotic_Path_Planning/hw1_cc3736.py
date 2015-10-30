__author__ = "Chao Chen"
__email__ = "cc3736@columbia.edu"

import argparse
import math
from random import*
import time

parser = argparse.ArgumentParser(description='Robot Path Planning | HW 1 | COMS 4701')
parser.add_argument('-bfs', action="store_true", default=False, help="Run BFS on the map")
parser.add_argument('-dfs', action="store_true", default=False, help="Run DFS on the map")
parser.add_argument('-astar', action="store_true", default=False, help="Run A* on the map")
parser.add_argument('-ida', action="store_true", default=False, help="Run IDA* on the map")
parser.add_argument('-all', action="store_true", default=False, help="Run all the 3 algorithms")
parser.add_argument('-m', action="store", help="Map filename")

results = parser.parse_args()

if results.m == "" or not (results.all or results.astar or results.bfs or results.dfs or results.ida):
    print "Check the parameters : >> python hw1_UNI.py -h"
    exit()

if results.all:
    results.bfs = results.dfs = results.astar = results.ida = True

output_file = "hw1_output" + results.m[5] + ".txt"

# Reading of map given and all other initializations
try:
    with open(results.m) as f:
        arena = f.read()
        arena = arena.split("\n")[:-1]
    open(output_file, 'wt').close()
except:
    print "Error in reading the arena file."
    exit()

# Internal representation
# print arena
print "The arena of size " + str(len(arena)) + "x" + str(len(arena[0]))
print "\n".join(arena)

# locate the start and goal
for i in range(0, len(arena)):
    for j in range(0, len(arena[0])):
        if arena[i][j] == 's':
            start = {'axis': [i, j], 'last_node': None, 'g_cost': 0, 'f_cost': 0.0}
        elif arena[i][j] == 'g':
            goal = {'axis': [i, j], 'last_node': None}


def goal_test(axis):
    return axis == goal.get('axis')


# This method is used to test whether the node has been explored or not
# by inputting the coordinates.
#
# return true if available to step on
#
# return false if the node is in frontier list, or
# in explored list or occupied by barriers or out of the map

def is_unexplored(axis,_frontier_=[],_explored_=[]):
    if axis[0] < 0 or axis[0] >= len(arena) or axis[1] < 0 or axis[1] >= len(arena[0]):
        return False
    if arena[axis[0]][axis[1]] == 'o':
        return False
    for each in _frontier_:
        if axis == each.get('axis'):
            return False
    for each in _explored_:
        if axis == each.get('axis'):
            return False
    return True


# Print the route of the searching algorithm and save to file
def print_and_save(node, algorithm):
    count = -1
    content = arena[:]
    while node is not None:
        count += 1
        str_temp = ''
        # replace the whole row with '*' replaced
        for i in range(0, len(content[0])):
            if node.get('axis')[1] == i and content[node.get('axis')[0]][node.get('axis')[1]] == ' ':
                str_temp += '*'
            else:
                str_temp += content[node.get('axis')[0]][i]
        content[node.get('axis')[0]] = str_temp
        node = node.get('last_node')
    content = "\n".join(content)
    if count == -1:
        count = "Goal Unreachable"
    content += "\n" + algorithm.upper() + ": " + str(count) + "\n"
    print content
    try:
        with open(output_file, 'a') as fw:
            fw.write(content)
    except:
        print "Error in writing the output file"
        exit()


# generate a random list of next steps.
# Shuffle the sequence of 'up' 'left' 'down' 'right'
def child_list(axis):
    child = [[axis[0]+1, axis[1]], [axis[0], axis[1]+1], [axis[0]-1, axis[1]], [axis[0], axis[1]-1]]
    shuffle(child)  # random sequence
    return child


def bfs_search():
    num = 0   # Used for counting Memory requirement
    frontier = list()
    explored = list()
    frontier.append(start)
    while frontier.__len__() is not 0:
        if frontier.__len__()+explored.__len__()>num:
            num = frontier.__len__()+explored.__len__()
        node = frontier.pop(0)
        explored.append(node)
        for each_axis in child_list(node.get("axis")):
            if is_unexplored(each_axis, frontier, explored):
                if goal_test(each_axis):
                    print "BFS:\nTotal memory use(node): ", str(num)
                    return {'axis': each_axis, 'last_node': node}
                else:
                    frontier.append({'axis': each_axis, 'last_node': node})
    return None


def dfs_search():
    frontier = list()
    explored = list()
    frontier.append(start)
    num = 0 # Used for counting Memory Requirement
    while frontier.__len__() is not 0:
        if frontier.__len__()+explored.__len__() > num:
            num = frontier.__len__()+explored.__len__()
        node = frontier.pop()
        if goal_test(node.get('axis')):
            print "DFS:\nTotal memory use(node): ", str(num)
            return node
        else:
            explored.append(node)
            x=node.get("axis")[0]
            y=node.get("axis")[1]
            for each_axis in [[x,y-1],[x-1,y],[x,y+1],[x+1,y]]:
                if is_unexplored(each_axis, frontier,explored):
                    frontier.append({'axis': each_axis, 'last_node': node})
    return None


def f(x):
    return x.get('f_cost')


# here I implement graph-search a*, it's optimal because the cost over the path is non-decreasing
def a_star_search():
    frontier = list()
    explored = list()
    frontier.append(start)
    num = 0  # Used for counting memory requirement
    while frontier.__len__() is not 0:
        frontier.sort(key=f)
        node = frontier.pop(0)
        if frontier.__len__() + explored.__len__() > num:
            num = frontier.__len__() + explored.__len__()
        if goal_test(node.get('axis')):
            print "A*:\nTotal memory use(node): ", str(num)
            return node
        else:
            explored.append(node)
            for each in child_list(node.get("axis")):
                if is_unexplored(each, frontier, explored):  # Critical for graph-search a* algorithm. Involves open set and close set.
                    frontier.append({'axis': each, 'last_node': node,
                                     'g_cost': (node.get('g_cost') + 1),
                                     'f_cost': node.get("g_cost") + abs(each[0]-goal.get("axis")[0]) + abs(each[1]-goal.get("axis")[1])})
    return None


def ida_search():
    path_limit_ = 0
    num = 0
    while 1:
        frontier = list()
        frontier.append(start)
        path_limit_next = len(arena)*len(arena[0])
        while frontier.__len__() is not 0:
            node = frontier.pop(0)
            if frontier.__len__()>num:
                num = frontier.__len__()
            if goal_test(node.get('axis')):
                print "IDA*:\nTotal memory use(node): ", str(num)
                return node
            elif node.get("f_cost") <= path_limit_:
                for each in child_list(node.get("axis")):
                    if is_unexplored(each, frontier):
                        f_cost = node.get("g_cost") + abs(each[0]-goal.get("axis")[0]) + abs(each[1]-goal.get("axis")[1])
                        if path_limit_ < f_cost < path_limit_next:
                            path_limit_next = f_cost
                        frontier.append({'axis': each, 'last_node': node,
                                         'g_cost': (node.get('g_cost') + 1),
                                         'f_cost': f_cost})
        path_limit_ = path_limit_next
    return None


# The main process starts here
if results.bfs:
    time1 = time.time()
    solution = bfs_search()
    time2 = time.time()
    print "BFS Time cost: ", str(time2-time1)

    print_and_save(solution, "bfs")


if results.dfs:
    time1 = time.time()
    solution = dfs_search()
    time2 = time.time()
    print "DFS Time cost: ", str(time2-time1)

    print_and_save(solution, "dfs")


if results.astar:
    time1 = time.time()
    solution = a_star_search()
    time2 = time.time()
    print "A* Time cost: ", str(time2-time1)

    print_and_save(solution, "a*")


if results.ida:
    solution = None
    try:
        time1 = time.time()
        solution = ida_search()
        time2 = time.time()
        print "IDA* Time cost: ", str(time2-time1)
    except:
        {}
    print_and_save(solution, "ida")


