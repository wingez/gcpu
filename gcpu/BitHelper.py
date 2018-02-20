def nthbyte(data, n):
    mask = 0xff << ((n - 1) * 8)
    masked = mask & data
    return masked >> ((n - 1) * 8)


firstbyte = lambda data: nthbyte(data, 1)
secondbyte = lambda data: nthbyte(data, 2)
thirdbyte = lambda data: nthbyte(data, 3)
fourthbyte = lambda data: nthbyte(data, 4)

uppernibble = lambda data: (data & 0xf0) >> 4
lowernibble = lambda data: data & 0x0f

touppernibble = lambda data: (data & 0x0f) << 4
tolowernibble = lambda data: data & 0x0f


def bitbuilder(*args):
    if type(args) is not tuple:
        return lambda i: i & masknbits(args)

    sizes = []
    offsets = []
    offset = 0
    for i in args:
        sizes.append(i)
        offsets.append(offset)
        offset += i

    def resultfunc(*numbers):
        if len(numbers) != len(sizes):
            raise ValueError('To few/many arguments')
        result = 0
        for number, size, offset in zip(numbers, sizes, offsets):
            result |= ((masknbits(size) & number) << offset)
        return result


def masknbits(n):
    if n == 0:
        return 0
    result = 1
    for k in range(n - 1):
        result <<= 1
        result |= 1
    return result


def maskrange(start, stop):
    result = masknbits(stop - start)
    result <<= start
    return result
