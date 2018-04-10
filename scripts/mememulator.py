from . import bitbang


def Run(file, pinsfile):
    print('initializing memoryemulator')
    inputpins = bitbang.readpins(pinsfile, 'microcodein')
    outputpins = bitbang.readpins(pinsfile, 'microcodeout')

    data = [0] * (2 ** 15)
    with open(file, 'r') as f:
        for line in f:
            line = line.partition('#')[0]
            if not line:
                continue

            address, value = map(int, line.split())
            data[address] = value

    print("starting memoryemulator listener, CTRL+C to stop")

    prevaddress = -1

    try:
        while True:
            addr = bitbang.shiftin(16, pins=inputpins)

            if addr != prevaddress:
                prevaddress = addr

                signals = data[addr]

                bitbang.shiftout(signals, 32, outputpins)


    except KeyboardInterrupt:
        pass

    print("memoryemulator listener stopped")
