
def SignalMultiplexer(signals):
    bits = len(signals)

    def result(index):
        if index >=2**bits or index<0:
            raise ValueError('Index not in bounds')
        tmp=[]
        for i in range(bits):
            if (1<<i) & index:
                tmp.append(signals[i])
        return tmp

    return result

    

