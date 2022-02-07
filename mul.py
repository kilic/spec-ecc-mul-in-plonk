from random import randint
from utils import *
from ops import *


def mul_msb(point, scalar, n=0):
    reset_counters()

    if scalar == 0:
        return 0

    bits = decompose(scalar, n)
    bits.reverse()

    aux_to_add = randint(1, (1 << n) - 1)
    aux_to_sub = aux_to_add * ((1 << n) - 1)

    table = make_incremantal_table(point, 1, aux_to_add)
    acc = select([bits[0]], table)
    for b in bits[1:]:
        acc = ladder(acc, select([b], table))

    acc = add(acc, -aux_to_sub)
    report_cost("msb")

    assert acc == point * scalar
    return acc


def mul_msb_general(
    point,
    scalar,
    window_size,
    n=0,
):

    reset_counters()
    info("msb general", window_size)

    if scalar == 0:
        return 0

    bits = decompose(scalar, n)
    bits.reverse()

    windowed = window(bits, window_size, "big")
    selectors = [rev(w) for w in windowed]

    aux_to_add = randint(1, (1 << n) - 1)
    k = 1
    for i in range(len(selectors)):
        k |= (1 << (i * window_size))
    aux_to_sub = aux_to_add * k

    table = make_incremantal_table(point, window_size, aux_to_add)
    cost_0 = report_cost("precomputation")

    acc = select(selectors[0], table)
    for selector in selectors[1:]:
        acc = double(acc, window_size - 1)
        acc = ladder(acc, select(selector, table))

    cost_1 = report_cost("iteration")
    res = add(acc, -aux_to_sub)
    cost_2 = report_cost("final")

    info("total cost", cost_0 + cost_1 + cost_2)

    assert res == point * scalar
    return res


def mul_msb_general_depreciated(
    point,
    scalar,
    window_size,
    n=0,
):

    reset_counters()
    if scalar == 0:
        return 0

    bits = decompose(scalar, n)
    bits.reverse()

    windowed = window(bits, window_size, "big")
    selectors = [rev(w) for w in windowed]
    table = make_incremantal_table(point, window_size, 0)

    aux = randint(1, (1 << n) - 1)
    acc = aux
    cost_0 = report_cost("precomputation")
    acc = add(acc, select(selectors[0], table))
    for selector in selectors[1:]:
        acc = double(acc, window_size - 1)
        acc = ladder(acc, select(selector, table))

    cost_1 = report_cost("iteration")
    number_of_doubling = (len(selectors) - 1) * window_size

    aux_final = double_constant(aux, number_of_doubling)
    res = add(acc, -aux_final)
    cost_2 = report_cost("final")

    info("total cost", cost_0 + cost_1 + cost_2)

    assert res == point * scalar
    return res


def mul_lsb(point, scalar, n=0):
    reset_counters()

    if scalar == 0:
        return 0

    bits = decompose(scalar, n)
    aux = randint(1, (1 << n) - 1)

    powers = point
    table = [aux, powers + aux]
    acc = select([bits[0]], table)

    for b in bits[1:]:
        powers = double_constant(powers)
        table = [aux, powers + aux]
        acc = add(acc, select([b], table))

    acc = add(acc, -aux * n)
    report_cost("lsb")
    assert acc == point * scalar
    return acc


def test():
    iter = 100
    for _ in range(iter):
        n = 256
        a = randint(0, (1 << n) - 1)
        b = randint(0, (1 << n) - 1)
        mul_msb(a, b, n)
        mul_lsb(a, b, n)

        mul_msb_general(a, b, 1, n)
        mul_msb_general(a, b, 2, n)
        mul_msb_general(a, b, 3, n)
        mul_msb_general(a, b, 4, n)
        mul_msb_general(a, b, 5, n)
        mul_msb_general(a, b, 6, n)
        mul_msb_general(a, b, 7, n)


test()

# print("var base mul cost")
# for w in range(1, 10):
#     window_size = w
#     table_size = 1 << window_size
#     number_of_bits = 256
#     number_of_iter = (number_of_bits // window_size) + 1

#     precomputation_cost = table_size * cost_add

#     number_of_selection_per_iter = table_size - 1
#     number_of_doubles_per_iter = w - 1

#     cost_per_iter = number_of_selection_per_iter * cost_select + number_of_doubles_per_iter * cost_double + cost_ladder
#     iteration_cost = cost_per_iter * number_of_iter
#     print("window", w, "cost", iteration_cost + precomputation_cost)

# print("fix base mul cost")
# for w in range(1, 10):
#     window_size = w
#     table_size = 1 << window_size
#     number_of_bits = 256
#     number_of_iter = (number_of_bits // window_size) + 1

#     precomputation_cost = table_size * cost_add

#     number_of_selection_per_iter = table_size - 1

#     cost_per_iter = number_of_selection_per_iter * cost_select + cost_add
#     iteration_cost = cost_per_iter * number_of_iter
#     print("window", w, "cost", iteration_cost + precomputation_cost)
