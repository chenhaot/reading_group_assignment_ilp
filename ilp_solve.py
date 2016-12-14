# -*- coding: utf-8 -*-

import collections
import csv
import numpy as np
import pulp
import argparse

def load_preference(filename):
    preference = {}
    group_list = []
    user_list = []
    with open(filename) as fin:
        reader = csv.reader(fin)
        header = True
        for row in reader:
            if header:
                header = False
                group_list = [v[v.find("[")+1:-1] for v in row[3:]]
            else:
                user = "%s,%s" % (row[1], row[2])
                user_list.append(user)
                preference[user] = {}
                for (g, v) in zip(group_list, row[3:]):
                    preference[user][g] = int(v)
    return preference, user_list, group_list


def find_best_assignment(user_list, group_list, preference):
    average = len(user_list) / 3
    model = pulp.LpProblem('assignment problem', pulp.LpMinimize)
    assignment = pulp.LpVariable.dicts('assignment', (user_list, group_list),
            lowBound=0, upBound=1, cat=pulp.LpInteger)
    group_chosen = pulp.LpVariable.dicts('chosen', group_list,
            lowBound=0, upBound=1, cat=pulp.LpInteger)
    model += sum([preference[u][g] * assignment[u][g]
        for u in user_list
        for g in group_list])
    # constraints: each person in a group
    for u in user_list:
        model += sum([assignment[u][g] for g in group_list]) == 1
    # constraints only three groups chosen
    model += sum([group_chosen[g] for g in group_list]) == 3
    # constraints each group with similar number of people
    for g in group_list:
        model += (sum([assignment[u][g] for u in user_list]) - average * group_chosen[g] ) >= 0
        model += (sum([assignment[u][g] for u in user_list]) - (average + 1) * group_chosen[g] ) <= 0
    model.solve()
    return assignment, group_chosen

def output_result(user_list, group_list, assignment, output_file):
    group_results = collections.defaultdict(list)
    for u in user_list:
        for g in group_list:
            if assignment[u][g].value() == 1:
                group_results[g].append(u)
    with open(output_file, "w") as fout:
        for key in group_results:
            fout.write("%s\n" % key)
            for user in group_results[key]:
                fout.write("%s\n" % user)
            fout.write("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str,
        help="input preferences in csv format from google forms")
    parser.add_argument("-o", "--output", type=str,
        help="output file for assignments")
    args = parser.parse_args()
    
    preference, user_list, group_list = load_preference(args.input)
    assignment, group_chosen = find_best_assignment(user_list, group_list, preference)
    output_result(user_list, group_list, assignment, args.output)

