
class Register(object):
    def __init__(self,index,name,read,write,description=''):
        self.index = index
        self.name = name

        self.read=read
        self.write=write
    def __str__(self):
        return self.name or 'register'
    def compileread(self):
        return BitHelper.touppernibble(self.index)
    def compilewrite(self):
        return BitHelper.tolowernibble(self.index)
