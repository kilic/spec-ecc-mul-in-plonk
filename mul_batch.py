from utils import *
from ops import cross_combine, info, make_incremantal_table, report_cost, reset_counters, select, add, ladder, double, combine


def multiexp_naive(pairs):
    acc = 0
    for (e, s) in pairs:
        acc += e * s
    return acc


def multiexp_1d_msb_horizontal(pairs, window_size, n):
    reset_counters()

    assert len(pairs) > 0

    offset = -n % window_size
    n = n + offset
    number_of_windows = n // window_size

    # decompose all scalars
    decomposed_scalars = [decompose(scalar, n) for (_, scalar) in pairs]

    windowed_scalars = [
        window(rev(decomposed), window_size, "big")
        for decomposed in decomposed_scalars
    ]

    # example for window_size = 2

    # decomposed_scalars:
    # a0 = [1, 0, 1, 0, ... ]
    # a1 = [0, 1, 1, 0, ... ]
    # a2 = [0, 1, 1, 0, ... ]

    # selectors:
    # s0 = [[1, 0], [1, 0], ... ]
    # s1 = [[0, 1], [1, 0], ... ]
    # s2 = [[0, 1], [1, 0], ... ]

    # prepare tables
    # table_entry = [0, a0, 2a0, 3a0]

    tables = [
        make_incremantal_table(point, window_size, 0) for point, _ in pairs
    ]

    acc = 0
    for j in range(len(pairs)):
        selector = rev(windowed_scalars[j][0])
        table = tables[j]
        to_add = select(selector, table)
        acc = add(to_add, acc)
    for i in range(1, number_of_windows):
        acc = double(acc, window_size)
        for j in range(len(pairs)):
            selector = rev(windowed_scalars[j][i])
            table = tables[j]
            to_add = select(selector, table)
            acc = add(to_add, acc)

    assert acc == multiexp_naive(pairs)
    return acc


def multiexp_1d_msb_vertical(pairs, window_size, n):
    reset_counters()

    assert len(pairs) > 0

    offset = -len(pairs) % window_size
    # pad pairs into perfect size for the window
    pairs += [(0, 0)] * offset
    number_of_windows = len(pairs) // window_size

    # decompose all scalars
    decomposed_scalars = [decompose(scalar, n) for (_, scalar) in pairs]

    # example for window_size = 3

    # decomposed_scalars:
    # a0 = [1, 0, 1, 0, ... ]
    # a1 = [0, 1, 1, 0, ... ]
    # a2 = [0, 1, 1, 0, ... ]

    # selectors:
    # s0,  s1,  s2,  s3,  ...
    # |1|, |0|, |1|, |0|, ...
    # |0|, |1|, |1|, |0|, ...
    # |0|, |1|, |1|, |0|, ...

    selectors = []
    for i in range(n):
        entries = []
        for j in range(number_of_windows):
            window = decomposed_scalars[j * window_size:(j + 1) * window_size]
            entries.append([slice[i] for slice in window])

        selectors.append(entries)
    selectors.reverse()

    # prepare tables
    # table_entry_0 = [0, a0, a1, a2, a0 + a1, a0 + a2, a1 + a2, a1 + a2 + a3]

    tables = []
    for i in range(number_of_windows):
        points = [pairs[i * window_size + j][0] for j in range(window_size)]
        tables.append(combine(points))

    acc = 0
    for w in range(number_of_windows):
        to_add = select(selectors[0][w], tables[w])
        acc = add(acc, to_add)

    for selector in selectors[1:]:
        for i, w in enumerate(range(number_of_windows)):
            to_add = select(selector[w], tables[w])
            if i == 0:
                acc = ladder(acc, to_add)
            else:
                acc = add(acc, to_add)

    assert acc == multiexp_naive(pairs)
    return acc


def multiext_2d_msb(pairs, vertical_window_size, horizontal_window_size, n):
    reset_counters()

    assert len(pairs) > 0

    v_w = vertical_window_size
    h_w = horizontal_window_size

    vertical_offset = -len(pairs) % v_w
    # pad pairs into perfect size for the window
    pairs += [(0, 0)] * vertical_offset
    number_of_vertical_windows = len(pairs) // v_w

    # decompose all scalars
    horizontal_offset = -n % horizontal_window_size
    n = n + horizontal_offset
    iter_size = n // horizontal_window_size
    decomposed_scalars = [decompose(scalar, n) for (_, scalar) in pairs]

    windowed_scalars = [
        rev(window(bits, horizontal_window_size, "big"))
        for bits in decomposed_scalars
    ]

    # example for vertical_window_size = 3, horizontal_window_sze = 2

    # decomposed_scalars:
    # a0 = [1, 0, 1, 0, ... ]
    # a1 = [0, 1, 1, 0, ... ]
    # a2 = [0, 1, 1, 0, ... ]

    # windowed scalars:
    # w0,     w1,     ...
    # [1, 0], [1, 0], ...
    # [0, 1], [1, 0], ...
    # [0, 1], [1, 0], ...

    # selectors:
    # s0 = flat(w0) = [0, 1, 0, 1, 1, 0]
    # s1 = flat(w1) = [1, 0, 1, 0, 1, 0]

    selectors_2d = []

    for i in range(iter_size):  # horizontal

        entries = []
        for j in range(number_of_vertical_windows):  # vertical
            windows = windowed_scalars[j * v_w:(j + 1) * v_w]
            slice = [slice[i] for slice in windows]
            entries.append(flatten(slice))

        selectors_2d.append(entries)

    tables_1d = [make_incremantal_table(point, h_w, 0) for (point, _) in pairs]

    tables_2d = []
    for i in range(number_of_vertical_windows):
        offset0 = i * v_w
        offset1 = (i + 1) * v_w
        tables_slice = tables_1d[offset0:offset1]
        table = cross_combine(tables_slice)
        tables_2d.append(table)

    acc = 0
    number_of_iter = n // horizontal_window_size

    def addition_step(acc, selectors):
        for table, selector in zip(tables_2d, selectors):
            acc = add(acc, select(selector, table))
        return acc

    acc = addition_step(0, selectors_2d[0])

    for i in range(1, number_of_iter):
        acc = double(acc, horizontal_window_size)
        acc = addition_step(acc, selectors_2d[i])

    assert acc == multiexp_naive(pairs)
    return acc


def rand_pair(n):
    from random import randint
    point = randint(0, 1 << n)
    scalar = randint(0, 1 << n)
    return (point, scalar)


def test_2d():

    n = 256
    for number_of_pairs in range(1000, 1001):
        pairs = [rand_pair(n) for _ in range(number_of_pairs)]
        for h_w in range(1, 4):
            for v_w in range(1, 4):

                reset_counters()
                multiext_2d_msb(pairs, v_w, h_w, n)
                info("horiztal:", h_w)
                info("vertical:", v_w)
                info("number_of_paris:", number_of_pairs)
                report_cost("2d", number_of_pairs)


def test_1d_vertical():

    n = 256
    iter = 1

    for _ in range(iter):
        for window_size in range(1, 10):
            for number_of_pairs in range(200, 201):
                pairs = [
                    rand_pair(number_of_pairs) for _ in range(number_of_pairs)
                ]
                reset_counters()
                multiexp_1d_msb_vertical(pairs, window_size, n)
                info("window_size:", window_size)
                info("number_of_pairs:", number_of_pairs)
                report_cost("1dv", number_of_pairs)


def test_1d_horizontal():

    n = 256
    iter = 1

    for _ in range(iter):
        for window_size in range(1, 10):
            for number_of_pairs in range(200, 201):
                pairs = [
                    rand_pair(number_of_pairs) for _ in range(number_of_pairs)
                ]
                reset_counters()
                multiexp_1d_msb_horizontal(pairs, window_size, n)
                info("window_size:", window_size)
                info("number_of_paris:", number_of_pairs)
                report_cost("1dh", number_of_pairs)


test_1d_horizontal()
test_1d_vertical()
test_2d()
