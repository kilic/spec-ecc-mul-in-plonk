# Operations

cost_double = 200
cost_add = 200
cost_ladder = 300
cost_select = 10  # five width equation with 2 multiplication gate
# cost_select = 23 # four width equation with 1 multiplication gate

count_double = 0
count_add = 0
count_select = 0
count_ladder = 0

should_report = True


def reset_counters():
    global count_double
    global count_add
    global count_select
    global count_ladder

    count_double = 0
    count_add = 0
    count_select = 0
    count_ladder = 0


def info(desc, n):
    if should_report:
        print(desc, n)


def report_cost(desc, n=1):

    # print("double ", count_double)
    # print("add    ", count_add)
    # print("select ", count_select)
    # print("ladder ", count_ladder)
    cost = count_double * cost_double + count_add * cost_add + count_ladder * cost_ladder + count_select * cost_select
    if should_report:
        print(desc, "cost", cost)
        print(desc, "cost/n", cost // n)
    reset_counters()
    return cost


def double(e, n=1):
    global count_double
    count_double += n
    return e << n


def double_constant(e, n=1):
    return e << n


def double_incomplete(e, n=1):
    assert e != 0
    return double(e, n)


def add(a, b):
    global count_add
    count_add += 1
    return a + b


def add_incomplete_unsafe(a, b):
    assert a != 0
    assert b != 0
    assert a != b
    return add(a, b)


def ladder(to_double, to_add):
    # assert to_double != 0
    # assert to_add != 0
    global count_ladder
    count_ladder += 1
    return to_double + to_add + to_double


def select(c, table):
    select = lambda c, a0, a1: a1 if c else a0

    w = len(c)
    assert len(table) == 1 << w

    global count_select
    count_select += len(table) - 1

    u = table[:]
    for i in range(w):
        n = 1 << (w - 1 - i)
        u = [select(c[i], u[2 * j], u[2 * j + 1]) for j in range(n)]

    assert len(u) == 1
    return u[0]


def combine(elements):
    combinations = [0]
    for e in elements:
        to_append = []
        for s in combinations:
            to_append.append(add(s, e))
        combinations += to_append
    return combinations


def make_incremantal_table(point, window_size, aux):
    global count_add
    count_add += window_size
    return [aux + point * u for u in range(1 << window_size)]


def cross_combine(tables):

    n = len(tables)

    global count_add
    count_add += (1 << n) - n - 1

    assert n > 0
    w = len(tables[0])
    for table in tables:
        assert len(table) == w

    l = w**n

    combinations = []
    for i in range(l):
        indexes = [(i // (w**j)) % w for j in range(n)]
        combination = sum([table[i] for table, i in zip(tables, indexes)])
        combinations.append(combination)

    return combinations
