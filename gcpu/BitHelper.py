



def nthbyte(data,n):
    mask = 0xff << ((n - 1) * 8)
    masked = mask & data
    return masked >> ((n - 1) * 8)



firstbyte = lambda data:nthbyte(data,1)
secondbyte = lambda data:nthbyte(data,2)
thirdbyte = lambda data:nthbyte(data,3)
fourthbyte = lambda data:nthbyte(data,4)



uppernibble = lambda data:(data & 0xf0) >> 4
lowernibble = lambda data:data & 0x0f

touppernibble = lambda data:(data & 0x0f) << 4
tolowernibble = lambda data:data & 0x0f









