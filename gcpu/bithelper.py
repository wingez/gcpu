from itertools import accumulate, chain


def nbyte(data, n):
    mask = 0xff << ((n - 1) * 8)
    masked = mask & data
    return masked >> ((n - 1) * 8)


# def firstbyte(i):
#    return nbyte(i, 1)


# firstbyte = lambda data: nthbyte(data, 1)
# secondbyte = lambda data: nbyte(data, 2)
# thirdbyte = lambda data: nbyte(data, 3)
# fourthbyte = lambda data: nbyte(data, 4)

uppernibble = lambda data: (data & 0xf0) >> 4
lowernibble = lambda data: data & 0x0f

touppernibble = lambda data: (data & 0x0f) << 4
tolowernibble = lambda data: data & 0x0f


def bitbuilder(*args):
    data = {}
    offset = 0
    for name, size in args:
        data[name] = (size, offset)
        offset += size

    def resultfunc(**kwargs):

        result = 0
        for name, value in kwargs.items():
            size = data[name][0]
            offset = data[name][1]

            result |= ((masknbits(size) & value) << offset)
        return result

    return resultfunc


def masknbits(n):
    return (2 << n) - 1


def maskrange(start, stop):
    result = masknbits(stop - start)
    result <<= start
    return result
