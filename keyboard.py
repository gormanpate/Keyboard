#!/usr/bin/python3
# -*- coding: utf-8 -*-

# %%
import random
from typing import TypedDict
import math
import json
import datetime
import string


LEFT_DVORAK = "',.PY" "AOEUI" ";QJKX"
LEFT_QWERTY = "QWERT" "ASDFG" "ZXCVB"
LEFT_COLEMK = "QWFPG" "ARSTD" "ZXCVB"
LEFT_WORKMN = "QDRWB" "ASHTG" "ZXMCV"

LEFT_DISTAN = "22222" "11112" "22222"
LEFT_ERGONO = "11112" "11112" "22323"
LEFT_EDGE_B = "12345" "12345" "12345"

# Positions     56   7890123   456789   01234
RIGHT_DVORAK = "[]" "FGCRL/=" "DHTNS-" "BMWVZ"
RIGHT_QWERTY = "-=" "YUIOP[]" "HJKL;'" "NM,./"
RIGHT_COLEMK = "-=" "JLUY;[]" "HNEIO'" "KM,./"
RIGHT_WOKRMN = "-=" "JFUP;[]" "YNEOI'" "KL,./"

RIGHT_DISTAN = "34" "2222223" "211112" "22222"
RIGHT_ERGONO = "33" "3111134" "211112" "21222"
RIGHT_EDGE_B = "21" "7654321" "654321" "54321"

DVORAK = LEFT_DVORAK + RIGHT_DVORAK
QWERTY = LEFT_QWERTY + RIGHT_QWERTY
COLEMAK = LEFT_COLEMK + RIGHT_COLEMK
WORKMAN = LEFT_WORKMN + RIGHT_WOKRMN

DISTANCE = LEFT_DISTAN + RIGHT_DISTAN
ERGONOMICS = LEFT_ERGONO + RIGHT_ERGONO
PREFER_EDGES = LEFT_EDGE_B + RIGHT_EDGE_B

# Real data on w.p.m. for each letter, normalized.
# Higher values is better (higher w.p.m.)
with open(file="typing_data/manual-typing-data_qwerty.json", mode="r") as f:
    data_qwerty = json.load(fp=f)
with open(file="typing_data/manual-typing-data_dvorak.json", mode="r") as f:
    data_dvorak = json.load(fp=f)
data_values = list(data_qwerty.values()) + list(data_dvorak.values())
mean_value = sum(data_values) / len(data_values)
data_combine = []
for dv, qw in zip(DVORAK, QWERTY):
    if dv in data_dvorak.keys() and qw in data_qwerty.keys():
        data_combine.append((data_dvorak[dv] + data_qwerty[qw]) / 2)
    elif dv in data_dvorak.keys() and qw not in data_qwerty.keys():
        data_combine.append(data_dvorak[dv])
    elif dv not in data_dvorak.keys() and qw in data_qwerty.keys():
        data_combine.append(data_qwerty[qw])
    else:
        # Fill missing data with the mean
        data_combine.append(mean_value)


class Individual(TypedDict):
    genome: str
    fitness: int


Population = list[Individual]


def render_keyboard(individual: Individual) -> str:
    layout = individual["genome"]
    fitness = individual["fitness"]
    """Prints the keyboard in a nice way"""
    return (
        f"______________  ________________\n"
        f" ` 1 2 3 4 5 6  7 8 9 0 " + " ".join(layout[15:17]) + " Back\n"
        f"Tab " + " ".join(layout[0:5]) + "  " + " ".join(layout[17:24]) + " \\\n"
        f"Caps " + " ".join(layout[5:10]) + "  " + " ".join(layout[24:30]) + " Enter\n"
        f"Shift "
        + " ".join(layout[10:15])
        + "  "
        + " ".join(layout[30:35])
        + " Shift\n"
        f"\nAbove keyboard has fitness of: {fitness}"
    )


# <<<< DO NOT MODIFY


def initialize_individual(genome: str, fitness: int) -> Individual:
    indiv: Individual = {"genome": genome, "fitness": fitness}
    return indiv


def initialize_pop(example_genome: str, pop_size: int) -> Population:

    pop: Population = []
    temp_list = list(example_genome)
    for i in range(pop_size):
        random.shuffle(temp_list)
        temp_string = "".join(temp_list)
        indiv = initialize_individual(temp_string, 0)
        pop.append(indiv)
    return pop


def recombine_pair(parent1: Individual, parent2: Individual) -> Population:

    children: Population = []
    temp1 = ""
    temp2 = ""
    x = random.choice(range(len(parent1["genome"])))
    temp1 = parent1["genome"][:x] + parent2["genome"][x:]
    temp2 = parent2["genome"][:x] + parent1["genome"][x:]
    duplicate = parent1["genome"]
    for i in temp1:
        if i in duplicate:
            duplicate = duplicate.replace(i, "")
        else:
            temp_char = random.choice(duplicate)
            temp1 = temp1.replace(i, temp_char, 1)
            duplicate = duplicate.replace(temp_char, "")
    duplicate = parent1["genome"]
    for i in temp2:
        if i in duplicate:
            duplicate = duplicate.replace(i, "")
        else:
            temp_char = random.choice(duplicate)
            temp2 = temp2.replace(i, temp_char, 1)
            duplicate = duplicate.replace(temp_char, "")
    children.append(initialize_individual(temp1, 0))
    children.append(initialize_individual(temp2, 0))
    return children


def recombine_group(parents: Population, recombine_rate: float) -> Population:

    new_pop: Population = []

    for i in range(0, len(parents) - 1, 2):
        if random.random() < recombine_rate:
            temp: Population = recombine_pair(parents[i], (parents[i + 1]))
            new_pop.append(temp[0])
            new_pop.append(temp[1])
        else:
            new_pop.append(parents[i])
            new_pop.append(parents[i + 1])
    return new_pop


def mutate_individual(parent: Individual, mutate_rate: float) -> Individual:


    duplicate = parent["genome"]
    temp = ""
    for i in parent["genome"]:
        if random.random() < mutate_rate:
            temp = temp + (random.choice(parent["genome"]))
        else:
            temp = temp + i
    for i in temp:
        if i in duplicate:
            duplicate = duplicate.replace(i, "")
        else:
            x = random.choice(duplicate)
            temp = temp.replace(i, x, 1)
            duplicate = duplicate.replace(x, "")
    return initialize_individual(temp, 0)


def mutate_group(children: Population, mutate_rate: float) -> Population:

    pop: Population = []
    for i in children:
        pop.append(mutate_individual(i, mutate_rate))
    return pop


# DO NOT MODIFY >>>>
def evaluate_individual(individual: Individual) -> None:

    layout = individual["genome"]

    # Basic return to home row, with no differential cost for repeats.
    fitness = 0
    for pos, key in enumerate(layout):
        fitness += count_dict[key] * int(DISTANCE[pos])

    # Top-down guess at ideal ergonomics
    for pos, key in enumerate(layout):
        fitness += count_dict[key] * int(ERGONOMICS[pos])

    # Keybr.com querty-dvorak average data as estimate of real hand
    for pos, key in enumerate(layout):
        fitness += count_dict[key] / data_combine[pos]

    # Symbols should be toward edges.
    for pos, key in enumerate(layout):
        if key in "-[],.';/=":
            fitness += int(PREFER_EDGES[pos])

    # Vowels on the left, Consosants on the right
    for pos, key in enumerate(layout):
        if key in "AEIOUY" and pos > 14:
            fitness += 3

    # [] {} () <> should be adjacent.
    # () are fixed by design choice (number line).
    # [] and {} are on same keys.
    # Perhaps ideally, <> and () should be on same keys too...
    right_edges = [4, 9, 14, 16, 23, 29, 34]
    for pos, key in enumerate(layout):
        # order of (x or y) protects index on far right:
        if key == "[" and (pos in right_edges or "]" != layout[pos + 1]):
            fitness += 1
        if key == "," and (pos in right_edges or "." != layout[pos + 1]):
            fitness += 1

    # high transitional probabilities should be rolls or alternates?
    # ing, ch, th, the, etc?
    # Would need to build a new dataset of 2 and 3 char transitions?
    for pos in range(len(layout) - 1):
        if pos in right_edges:
            continue
        char1 = layout[pos]
        char2 = layout[pos + 1]
        dict_key = char1 + char2
        fitness -= count_run2_dict[dict_key]

    individual["fitness"] = fitness


# <<<< DO NOT MODIFY


def evaluate_group(individuals: Population) -> None:

    for i in individuals:
        evaluate_individual(i)


def rank_group(individuals: Population) -> None:

    individuals.sort(key=lambda x: x["fitness"], reverse=False)


def parent_select(individuals: Population, number: int) -> Population:

    pop: Population = []
    weight = []
    for i in range(len(individuals)):
        weight.append(individuals[i]["fitness"])
    temp: Population = random.choices(individuals, weights=weight, k=number)
    for i in range(number):
        pop.append(temp[i])
    return pop


def survivor_select(individuals: Population, pop_size: int) -> Population:

    rank_group(individuals)
    pop: Population = []

    for i in range(pop_size):
        pop.append(individuals[i])
    return pop


def evolve(example_genome: str, pop_size: int = 100) -> Population:


    pop: Population = initialize_pop(example_genome, pop_size)
    evaluate_group(pop)
    rank_group(pop)
    best_fitness = pop[0]["fitness"]
    perfect_fitness = 55
    counter = 0
    while counter < 10000:
        counter += 1
        parents = parent_select(pop, 80)
        children = recombine_group(parents, 0.8)
        mutate_rate = 0.1
        mutants = mutate_group(children, mutate_rate)
        evaluate_group(mutants)
        everyone = pop + mutants
        rank_group(everyone)
        pop = survivor_select(everyone, pop_size)
        if best_fitness != pop[0]["fitness"]:
            best_fitness = pop[0]["fitness"]
            print("Iteration number", counter, "with best individual", pop[0])
    return pop


seed = False

# DO NOT MODIFY >>>>
if __name__ == "__main__":
    divider = "===================================================="
    # Execute doctests to protect main:
    # import doctest

    # doctest.testmod()
    # doctest.testmod(verbose=True)

    if seed:
        random.seed(42)

    with open("corpus/counts.json") as fhand:
        count_dict = json.load(fhand)
    # print({k: v for k, v in sorted(count_dict.items(), key=lambda item: item[1], reverse=True)})
    # print("Above is the order of frequency of letters in English.")

    # print("Counts of characters in big corpus, ordered by freqency:")
    # ordered = sorted(count_dict, key=count_dict.__getitem__, reverse=True)
    # for key in ordered:
    #     print(key, count_dict[key])

    with open("corpus/counts_run2.json") as fhand:
        count_run2_dict = json.load(fhand)
    # print({k: v for k, v in sorted(count_run2_dict.items(), key=lambda item: item[1], reverse=True)})
    # print("Above is the order of frequency of letter-pairs in English.")

    print(divider)
    print(
        f"Number of possible permutations of standard keyboard: {math.factorial(len(DVORAK)):,e}"
    )
    print("That's a huge space to search through")
    print("The messy landscape is a difficult to optimize multi-modal space")
    print("Lower fitness is better.")

    print(divider)
    print("\nThis is the Dvorak keyboard:")
    dvorak = Individual(genome=DVORAK, fitness=0)
    evaluate_individual(dvorak)
    print(render_keyboard(dvorak))

    print(divider)
    print("\nThis is the Workman keyboard:")
    workman = Individual(genome=WORKMAN, fitness=0)
    evaluate_individual(workman)
    print(render_keyboard(workman))

    print(divider)
    print("\nThis is the Colemak keyboard:")
    colemak = Individual(genome=COLEMAK, fitness=0)
    evaluate_individual(colemak)
    print(render_keyboard(colemak))

    print(divider)
    print("\nThis is the QWERTY keyboard:")
    qwerty = Individual(genome=QWERTY, fitness=0)
    evaluate_individual(qwerty)
    print(render_keyboard(qwerty))

    print(divider)
    print("\nThis is a random layout:")
    badarr = list(DVORAK)
    random.shuffle(badarr)
    badstr = "".join(badarr)
    badkey = Individual(genome=badstr, fitness=0)
    evaluate_individual(badkey)
    print(render_keyboard(badkey))

    print(divider)
    input("Press any key to start")
    population = evolve(example_genome=DVORAK)

    print("Here is the best layout:")
    print(render_keyboard(population[0]))

    grade = 0
    if qwerty["fitness"] < population[0]["fitness"]:
        grade = 0
    if colemak["fitness"] < population[0]["fitness"]:
        grade = 50
    if workman["fitness"] < population[0]["fitness"]:
        grade = 60
    elif dvorak["fitness"] < population[0]["fitness"]:
        grade = 70
    else:
        grade = 80

    with open(file="results.txt", mode="w") as f:
        f.write(str(grade))

    with open(file="best.json", mode="w") as f:
        f.write(json.dumps(population[0]))

    with open(file="best.txt", mode="w") as f:
        f.write(render_keyboard(population[0]))
