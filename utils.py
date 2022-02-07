from tkinter import N


def compose(bits):

    acc = 0
    for i, b in enumerate(bits):
        assert b == 1 or b == 0
        base = 1 << i
        acc = acc + base * b
    return acc


def decompose(e, n=0):
    input = e
    bits = []
    while e > 0:
        bits.append(1 if e & 1 else 0)
        e = e >> 1

    assert compose(bits) == input

    if n > 0:
        bits = bits + [0] * (n - len(bits))

    assert compose(bits) == input

    return bits


def window(e, w, end="big"):
    assert w > 0

    assert end == "big" or end == "little"

    offset = -len(e) % w

    windowed = []

    if end == "big":
        e = [0] * offset + e
    if end == "little":
        e = e + [0] * offset

    n = len(e) // w
    for i in range(n):
        round = []
        for j in range(w):
            round.append(e[i * w + j])
        windowed.append(round)

    return windowed


def rev(u):
    u.reverse()
    return u


def flatten(t):
    return [item for sublist in t for item in sublist]
