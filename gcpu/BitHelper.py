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
    if type(args) is not tuple:
        return lambda i: i & masknbits(args)

    sizes = args
    offsets = [x for x in chain([0], accumulate(args))]

    def resultfunc(*numbers):
        if len(numbers) != len(sizes):
            raise ValueError('To few/many arguments')
        result = 0
        for number, size, offset in zip(numbers, sizes, offsets):
            result |= ((masknbits(size) & number) << offset)
        return result

    return resultfunc


def masknbits(n):
    return (2 << n) - 1


def maskrange(start, stop):
    result = masknbits(stop - start)
    result <<= start
    return result
