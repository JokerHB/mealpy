#!/usr/bin/env python
# ------------------------------------------------------------------------------------------------------%
# Created by "Thieu Nguyen" at 12:51, 18/03/2020                                                        %
#                                                                                                       %
#       Email:      nguyenthieu2102@gmail.com                                                           %
#       Homepage:   https://www.researchgate.net/profile/Thieu_Nguyen6                                  %
#       Github:     https://github.com/thieu1995                                                        %
#-------------------------------------------------------------------------------------------------------%

import numpy as np
from mealpy.optimizer import Optimizer


class BaseWHO(Optimizer):
    """
    My version of: Wildebeest Herd Optimization (WHO)
        (Wildebeest herd optimization: A new global optimization algorithm inspired by wildebeest herding behaviour)
    Link:
        http://doi.org/10.3233/JIFS-190495
    Noted:
        + Before updated old position, i check whether new position is better or not.
    """

    def __init__(self, problem, epoch=10000, pop_size=100, n_s=3, n_e=3, eta=0.15, local_move=(0.9, 0.3),
                        global_move=(0.2, 0.8), p_hi=0.9, delta=(2.0, 2.0), **kwargs):
        """
        Args:
            problem ():
            epoch (int): maximum number of iterations, default = 10000
            pop_size (int): number of population size, default = 100
            n_s (int): default = 3, number of exploration step
            n_e (int): default = 3, number of exploitation step
            eta (float): default = 0.15, learning rate
            local_move (list): default = (0.9, 0.3), (alpha 1, beta 1) - control local movement
            global_move (list): default = (0.2, 0.8), (alpha 2, beta 2) - control global movement
            p_hi (float): default = 0.9, the probability of wildebeest move to another position based on herd instinct
            delta (list): default = (2.0, 2.0) , (delta_w, delta_c) - (dist to worst, dist to best)
            **kwargs ():
        """
        super().__init__(problem, kwargs)
        self.nfe_per_epoch = pop_size
        self.sort_flag = False

        self.epoch = epoch
        self.pop_size = pop_size
        self.n_s = n_s
        self.n_e = n_e
        self.eta = eta
        self.local_move = local_move
        self.global_move = global_move
        self.p_hi = p_hi
        self.delta = delta

    def evolve(self, epoch):
        """
        Args:
            epoch (int): The current iteration
        """
        nfe_epoch = 0
        ## Begin the Wildebeest Herd Optimization process
        pop_new = []
        for i in range(0, self.pop_size):
            ### 1. Local movement (Milling behaviour)
            local_list = []
            for j in range(0, self.n_s):
                temp = self.pop[i][self.ID_POS] + self.eta * np.random.uniform() * np.random.uniform(self.problem.lb, self.problem.ub)
                pos_new = self.amend_position_faster(temp)
                local_list.append([pos_new, None])
            local_list = self.update_fitness_population(local_list)
            _, best_local = self.get_global_best_solution(local_list)
            temp = self.local_move[0] * best_local[self.ID_POS] + self.local_move[1] * (self.pop[i][self.ID_POS] - best_local[self.ID_POS])
            pos_new = self.amend_position_faster(temp)
            pop_new.append([pos_new, None])
        pop_new = self.update_fitness_population(pop_new)
        pop_new = self.greedy_selection_population(self.pop, pop_new)
        nfe_epoch += self.pop_size

        for i in range(0, self.pop_size):
            ### 2. Herd instinct
            idr = np.random.choice(range(0, self.pop_size))
            if self.compare_agent(pop_new[idr], pop_new[i]) and np.random.rand() < self.p_hi:
                temp = self.global_move[0] * pop_new[i][self.ID_POS] + self.global_move[1] * pop_new[idr][self.ID_POS]
                pos_new = self.amend_position_faster(temp)
                fit_new = self.get_fitness_position(pos_new)
                nfe_epoch += 1
                if self.compare_agent([pos_new, fit_new], pop_new[i]):
                    pop_new[i] = [pos_new, fit_new]

        _, best, worst = self.get_special_solutions(pop_new, worst=1)
        g_best, g_worst = best[0], worst[0]

        pop_child = []
        for i in range(0, self.pop_size):
            dist_to_worst = np.linalg.norm(pop_new[i][self.ID_POS] - g_worst[self.ID_POS])
            dist_to_best = np.linalg.norm(pop_new[i][self.ID_POS] - g_best[self.ID_POS])

            ### 3. Starvation avoidance
            if dist_to_worst < self.delta[0]:
                temp = pop_new[i][self.ID_POS] + np.random.uniform() * (self.problem.ub - self.problem.lb) * \
                       np.random.uniform(self.problem.lb, self.problem.ub)
                pos_new = self.amend_position_faster(temp)
                pop_child.append([pos_new, None])

            ### 4. Population pressure
            if 1.0 < dist_to_best and dist_to_best < self.delta[1]:
                temp = g_best[self.ID_POS] + self.eta * np.random.uniform(self.problem.lb, self.problem.ub)
                pos_new = self.amend_position_faster(temp)
                pop_child.append([pos_new, None])

            ### 5. Herd social memory
            for j in range(0, self.n_e):
                temp = g_best[self.ID_POS] + 0.1 * np.random.uniform(self.problem.lb, self.problem.ub)
                pos_new = self.amend_position_faster(temp)
                pop_child.append([pos_new, None])

        nfe_epoch += len(pop_child)
        self.nfe_per_epoch = nfe_epoch
        pop_child = self.update_fitness_population(pop_child)
        pop_child = self.get_sorted_strim_population(pop_child, self.pop_size)
        self.pop = self.greedy_selection_population(pop_new, pop_child)

