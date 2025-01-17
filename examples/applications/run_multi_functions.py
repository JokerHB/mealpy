#!/usr/bin/env python
# ------------------------------------------------------------------------------------------------------%
# Created by "Thieu" at 17:40, 06/11/2021                                                               %
#                                                                                                       %
#       Email:      nguyenthieu2102@gmail.com                                                           %
#       Homepage:   https://www.researchgate.net/profile/Nguyen_Thieu2                                  %
#       Github:     https://github.com/thieu1995                                                        %
# ------------------------------------------------------------------------------------------------------%

from mealpy.bio_based import SMA
import numpy as np


def obj_function(solution):

    def booth(x, y):
        return (x + 2*y - 7)**2 + (2*x + y - 5)**2

    def bukin(x, y):
        return 100 * np.sqrt(np.abs(y - 0.01 * x**2)) + 0.01 * np.abs(x + 10)

    def matyas(x, y):
        return 0.26 * (x**2 + y**2) - 0.48 * x * y

    return [booth(solution[0], solution[1]), bukin(solution[0], solution[1]), matyas(solution[0], solution[1])]


problem_dict1 = {
    "obj_func": obj_function,
    "lb": [-10, -10],
    "ub": [10, 10],
    "minmax": "min",
    "verbose": True,
    "obj_weight": [0.4, 0.1, 0.5]               # Define it or default value will be [1, 1, 1]
}

## Run the algorithm
model1 = SMA.BaseSMA(problem_dict1, epoch=100, pop_size=50, pr=0.03)
model1.solve()

## You can access them all via object "history" like this:
model1.history.save_global_objectives_chart(filename="hello/goc")
model1.history.save_local_objectives_chart(filename="hello/loc")
model1.history.save_global_best_fitness_chart(filename="hello/gbfc")
model1.history.save_local_best_fitness_chart(filename="hello/lbfc")
model1.history.save_runtime_chart(filename="hello/rtc")
model1.history.save_exploration_exploitation_chart(filename="hello/eec")
model1.history.save_diversity_chart(filename="hello/dc")
model1.history.save_trajectory_chart(list_agent_idx=[3, 5], list_dimensions=[2], filename="hello/tc")