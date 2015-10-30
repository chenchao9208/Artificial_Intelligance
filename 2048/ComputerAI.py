__author__ = "Chao Chen"
__email__ = 'cc3736@columbia.edu'
#!/usr/bin/env python
# coding:utf-8

from random import randint
from BaseAI import BaseAI
import time
import math

from Grid import Grid


smoothWeight = 1.1  # 0.5    0.1   0.1    1.1   1.1
monoWeight = 2.5  # 1.1    1.1   1.6    1.6    1.5
spaceWeight = 40.0  # 3.5 4.3    6.3   9.3  20   40.0
maxWeight = 7.0  # 0.6    3.0   3.0     3.0   7.0

# used to force tiles to merge
# e.g. value: 512>256+256
check_dict = {0: 0,
              2: 0,
              4: 0,
              8: 0,
              16: 0,
              32: 1,
              64: 3,
              128: 7,
              256: 16,
              512: 34,
              1024: 70,
              2048: 145,
              4096: 300,
              8192: 610,
              16384: 1240}


class ComputerAI(BaseAI):
    def getMove(self, grid):
        # initiate timeval
        time_start = time.clock()
        time_end = time.clock()
        timeval = time_end - time_start

        depth = 2
        cell = None
        value = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        # adjust time limit based on potential search tree branch measured by available cells
        # if the potential branch is large, limit the time scale tighter.
        scale = grid.getAvailableCells().__len__()
        #adjustable time scale based to potential branch scale
        # 0.03 0.05 0.065 0.08
        if scale >= 10:
            time_limit = 0.02
        elif 8 <= scale < 10:
            time_limit = 0.03
        elif 6 <= scale < 8:
            time_limit = 0.045
        else:
            time_limit = 0.06
        # iterative deepening depth-firth minimax with alpha-beta pruning and some extra pruning
        while timeval < time_limit:
            depth += 2
            print depth
            if depth >= 11: break

            # Apply Alpha-Beta search to find a solution
            # with the cutoff of a specific depth
            result = self.alpha_beta_search(grid, alpha, beta, depth)

            cur_cell = result.get("best_cell")
            cur_value = result.get("value")

            # update alpha. When doing iterative deepening depth first search,
            # if the solution on deeper node is not good as shallower node,
            # the tree will be pruned.
            beta = min(beta, cur_value)

            if cur_value < value:
                value = cur_value
                cell = cur_cell

            time_end = time.clock()
            timeval = time_end - time_start

        # To prevent the program from breaking down
        # if no solution is provided after calculation,
        # return a random one.
        if cell is None:
            available_cells = grid.getAvailableCells()
            cell = available_cells[randint(0, len(available_cells) - 1)]
        return cell

    def alpha_beta_search(self, grid, alpha, beta, depth):
        result = self.min_value(grid, alpha, beta, depth, 1)
        return result


    def min_value(self, grid, alpha, beta, depth, flag):
        #if the search has reached the leaf, return the value
        if depth <= 0:
            return {"value": self.evaluate(grid), "best_cell": None, "alpha": alpha, "beta": beta}

        grid_inserted = grid.clone()
        cell_candidates = grid.getAvailableCells()
        #shuffle(cell_candidates)
        # if it has no child not, return its value
        if cell_candidates is []:
            return {"value": self.evaluate(grid), "best_cell": None, "alpha": alpha, "beta": beta}
        available_cells_2 = self.extra_pruning(cell_candidates, grid_inserted, flag)
        # available_cells_4=self.extra_pruning(cell_candidates,grid_inserted,4)
        best_cell = None
        value = float("inf")
        depth -= 1
        for cell in available_cells_2:
            grid_inserted.setCellValue(cell, 2)

            child = self.max_value(grid_inserted, alpha, beta, depth, 0)
            child_value = child.get("value")

            if child_value < value:
                value = child_value
                best_cell = cell

            if value < alpha:
                return {"value": value, "best_cell": best_cell, "alpha": alpha, "beta": beta}

            beta = min(beta, value)

            grid_inserted.setCellValue(cell, 0)

        return {"value": value, "best_cell": best_cell, "alpha": alpha, "beta": beta}


    def max_value(self, grid, alpha, beta, depth, flag):
        #if the search has reached to the leaf, return the value
        if depth <= 0:
            return {"value": self.evaluate(grid), "best_move": None, "alpha": alpha, "beta": beta}

        value = float("-inf")
        best_move = None

        available_moves = grid.getAvailableMoves()
        depth -= 1

        #if it has no child node, return its value
        if available_moves is []:
            return {"value": self.evaluate(grid), "best_move": None, "alpha": alpha, "beta": beta}

        for move in available_moves:
            grid_moved = grid.clone()
            grid_moved.move(move)

            # slight extra pruning at the first level of search tree.
            #if flag == 0 and self.need_pruning(grid_moved):
            #    continue
            child = self.min_value(grid_moved, alpha, beta, depth, 0)
            child_value = child.get("value")

            if child_value > value:
                value = child_value
                best_move = move

            # deal with alpha beta
            if value > beta:
                return {"value": value, "best_move": best_move, "alpha": alpha, "beta": beta}

            alpha = max(alpha, value)
        # if the slight extra pruning has pruned all the children, abandon pruning and restore.
        #if flag == 1 and best_move is None:
        #    return self.max_value(grid, alpha, beta, depth + 1, 0)

        return {"value": value, "best_move": best_move, "alpha": alpha, "beta": beta}


    # Extra pruning used in "min_value" method apart from alpha-beta pruning.
    # A grid could have up to 15 places to insert cell.
    # Except from alpha-beta pruning, an extra pruning is needed on this stage.
    def extra_pruning(self, cell_candidates, grid_inserted, flag):
        if flag == 1 :
            return cell_candidates
        if cell_candidates.__len__() == 5 and (grid_inserted.map[0][:] == [0, 0, 0, 0]
                                               or grid_inserted.map[3][:] == [0, 0, 0, 0]
                                               or grid_inserted.map[:][0] == [0, 0, 0, 0]
                                               or grid_inserted.map[:][3] == [0, 0, 0, 0]):
            return cell_candidates
        if cell_candidates.__len__() < 4:
            return cell_candidates

        available_cells = []
        cell_value_pair = []
        for cell in cell_candidates:
            grid_inserted.setCellValue(cell, 2)
            #value = self.smoothness(grid_inserted) - self.islands(
            #    grid_inserted)  # +grid_inserted.getAvailableMoves().__len__()
            value = -self.islands(grid_inserted)
            cell_value_pair.append({"cell": cell, "value": value})
            grid_inserted.setCellValue(cell, 0)
        cell_value_pair.sort(key=self.f)
        least = cell_value_pair[0].get("value")
        for pair in cell_value_pair:
            if pair.get("value") == least:
                available_cells.append(pair.get("cell"))
            # elif cell_value_pair.__len__() > 2 and available_cells.__len__() < 3:
            # available_cells.append(pair.get("cell"))
            else:
                break
        return available_cells

    # Retrieve key used to sort list
    def f(self, x):
        return x.get("value")

    def evaluate(self, grid):
        score = self.monotonicity(grid) * monoWeight + self.space(grid) * spaceWeight \
                + self.smoothness(grid) * smoothWeight \
                + self.maxValue(grid) * maxWeight \
                + self.space(grid) * spaceWeight

        score = self.punish_and_bonus(grid, score)
        return score

    def monotonicity(self, grid):
        total = [0, 0, 0, 0]
        for i in xrange(4):
            for j in xrange(4):
                if grid.map[i][j] == 0:
                    val1 = 0
                else:
                    val1 = math.log(grid.map[i][j], 2)

                next_i = -1
                next_j = -1
                for next_i in xrange(i + 1, grid.size, 1):
                    if grid.map[next_i][j] != 0:
                        break

                for next_j in xrange(j + 1, grid.size, 1):
                    if grid.map[i][next_j] != 0:
                        break

                if next_j != -1 and grid.map[i][next_j] != 0:
                    val2 = math.log(grid.map[i][next_j], 2)
                    if val1 < val2:
                        total[0] += val2 - val1
                    else:
                        total[1] += val1 - val2
                if next_i != -1 and grid.map[next_i][j] != 0:
                    val2 = math.log(grid.map[next_i][j], 2)
                    if val1 < val2:
                        total[2] += val2 - val1
                    else:
                        total[3] += val1 - val2

        mono = max(total[0], total[1]) + max(total[2], total[3])
        if grid.getMaxTile() >= 1024:
            mono *= 1.4
        return mono

    def smoothness(self, grid):
        cell_map = grid.map
        smoothness = 0.0
        for i in xrange(4):
            for j in xrange(4):
                if cell_map[i][j] != 0:
                    value = math.log(cell_map[i][j], 2)
                    next_i = -1
                    next_j = -1
                    for next_i in xrange(i + 1, 4, 1):
                        if cell_map[next_i][j] != 0:
                            break
                    for next_j in xrange(j + 1, 4, 1):
                        if cell_map[i][next_j] != 0:
                            break
                    if next_i != -1 and cell_map[next_i][j] != 0:
                        target_value = math.log(cell_map[next_i][j], 2)
                        smoothness -= math.fabs(target_value - value)
                    if next_j != -1 and cell_map[i][next_j] != 0:
                        target_value = math.log(cell_map[i][next_j], 2)
                        smoothness -= math.fabs(target_value - value)
        return smoothness

    def maxValue(self, grid):
        return math.log(grid.getMaxTile(), math.e)

    def space(self, grid):
        count = 0
        for i in xrange(4):
            for j in xrange(4):
                if grid.map[i][j] == 0:
                    count += 1
        if count == 0:
            return 0
        return math.log(count, 2)

    def islands(self, grid):
        mask = [[0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]]
        count = 0
        for i in xrange(4):
            for j in xrange(4):
                if mask[i][j] == 0 and grid.map[i][j] != 0:
                    count += 1
                    mask = self.update_mask([i, j], grid.map, mask)
        return count

    def update_mask(self, axis, cell_map, mask):
        mask[axis[0]][axis[1]] = 1

        axis_list = [[axis[0], axis[1] + 1],
                     [axis[0], axis[1] - 1],
                     [axis[0] + 1, axis[1]],
                     [axis[0] - 1, axis[1]]]
        for each in axis_list:
            if (0 <= each[0] <= 3 and 0 <= each[1] <= 3) \
                    and mask[each[0]][each[1]] == 0 \
                    and cell_map[each[0]][each[1]] == cell_map[axis[0]][axis[1]] != 0:
                mask = self.update_mask(each, cell_map, mask)
        return mask

    #some other factors apart from weighted features
    def punish_and_bonus(self, grid, score):
        cell_list = []
        cell_map = grid.map
        for i in xrange(4):
            for j in xrange(4):
                cell_list.append({"axis": [i, j], "value": cell_map[i][j]})
        cell_list.sort(key=self.f)

        # edge_value_bonus = 0
        edge_value_bonus1 = 0
        tmp = cell_list.pop()
        axis = tmp.get("axis")
        first = tmp.get("value")
        second = cell_list.pop().get("value")
        third = cell_list.pop().get("value")
        fourth = cell_list.pop().get("value")
        fifth = cell_list.pop().get("value")
        if axis[0] != 0 and axis[0] != 3 and axis[1] != 0 and axis[1] != 3:
            score /= 6.0
            return score
        cell_sort = []
        if cell_map[0][0] == first:
            # edge_value_bonus += math.log(first,2)
            if second >= 16:
                if cell_map[0][1] == second:
                    cell_sort = [[0, 0], [0, 1], [0, 2], [0, 3], [1, 3]]
                elif cell_map[1][0] == second:
                    cell_sort = [[0, 0], [1, 0], [2, 0], [3, 0], [3, 1]]
        elif cell_map[0][3] == first:
            # edge_value_bonus += math.log(first,2)
            if second >= 16:
                if cell_map[0][2] == second:
                    cell_sort = [[0, 3], [0, 2], [0, 1], [0, 0], [1, 0]]
                elif cell_map[1][3] == second:
                    cell_sort = [[0, 3], [1, 3], [2, 3], [3, 3], [3, 2]]
        elif cell_map[3][0] == first:
            # edge_value_bonus += math.log(first,2)
            if second >= 16:
                if cell_map[3][1] == second:
                    cell_sort = [[3, 0], [3, 1], [3, 2], [3, 3], [2, 3]]
                elif cell_map[2][0] == second:
                    cell_sort = [[3, 0], [2, 0], [1, 0], [0, 0], [0, 1]]
        elif cell_map[3][3] == first:
            # edge_value_bonus += math.log(first,2)
            if second >= 16:
                if cell_map[3][2] == second:
                    cell_sort = [[3, 3], [3, 2], [3, 1], [3, 0], [2, 0]]
                elif cell_map[2][3] == second:
                    cell_sort = [[3, 3], [2, 3], [1, 3], [0, 3], [0, 2]]
        else:
            score /= 5.0
            return score

        if cell_sort.__len__() == 0:
            score /= 2.0
        else:
            # edge_value_bonus += math.log(second,2)
            if third != grid.getCellValue(cell_sort[2]):
                score /= 1.4
            else:
                #edge_value_bonus += math.log(third,2)

                if grid.getCellValue(cell_sort[3]) != 0:
                    #bonus
                    edge_value_bonus1 += 2 * math.log(grid.getCellValue(cell_sort[3]), 2)

                if grid.getCellValue(cell_sort[3]) != fourth:
                    score /= 1.1
                elif grid.getCellValue(cell_sort[4]) == fifth:
                    #bonus
                    score *= 1.2
        #bonus
        score += edge_value_bonus1
        score += 5 * check_dict.get(first)
        score += 5 * check_dict.get(second)
        score += 5 * check_dict.get(third)
        score += 5 * check_dict.get(fourth)
        score += 5 * check_dict.get(fifth)
        return score
