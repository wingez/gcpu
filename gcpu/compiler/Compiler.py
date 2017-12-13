import io
import Syntax

class CompileError(Exception):pass

fileextension='.txt'
programsize=2**15

registers={}
def SetRegisters(regissterlist):
    for r in regissterlist:
        registers[r.name]=r

def mergedicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def betterexec(statement,globals,locals):
    t = statement.partition('=')
    key = t[0].strip()
    value = eval(t[2],globals,locals)
    return (key,value)



class DependentConstant(object):
    def __init__(dependents):
        self.dependents = dependents

    def phase1op(self,other):
        if type(other) is int:
            return self
        else:
            return DependentConstant(self.dependents|other.dependents)

    def __add__(self,other):
        self.phase1op(other)

    def __sub__(self,other):
        self.phase1op(other)

class MemorySegment(object):
    def __init__(self):
        self.baseaddress = 0
        self.dependents = set()
        self.size=0
        self.content=[]
        self.sourcefile=None
        self.name=None
    def setcontent(self,content):
        if len(content) != self.size:
            raise CompileError('content not correct size')
        self.content=content
    
    def phase1op(self,other):
        if type(other) is int:
            return DependentConstant({self})
        else:
            return DependentConstant({self}|other.dependents)
    
    def __add__(self,other):
        if Compiler.phase==1:
            return self.phase1op(other)
        return self.baseaddress+other

    def __sub__(self,other):
        if Compiler.phase==1:
            return self.phase1op(other)
        return self.baseaddress-other
    
    def __str__(self):
        return '{}_{} base:{} size:{}'.format(self.sourcefile.name,self.name,self.baseaddress,self.size) 
class MemorysegmentContent(object):
    def __init__(self,content):
        self.content=content

class CodeBlock(object):

    def __init__(self,




class Compiler(object):

    includedfiles = {}
    toinclude = []
    
    phase = 0
    globalvariables={}
    
    
    def compile(filename):
        Compiler.phase = 0

        Compiler.globalvariables.update(registers)
    
    
        memsegmentmethods = {'ms':Compiler.ms} 
        Compiler.globalvariables.update(memsegmentmethods)



        basefile = FileCompiler(filename)
        toinclude = basefile.dependencies

        includedfiles={filename:basefile}


        while len(toinclude) > 0:
            pass

        Compiler.phase = 1

        for file in includedfiles.values():
            file.compilephase1()
        
        allmemsegements = []
            
        for file in includedfiles.values():
            allmemsegements+=file.memorysegments



        memsegmentstoadd=set()

        def addmemsegmentrecursive(memsegment):
            memsegmentstoadd.add(memsegment)
            for m in memsegment.dependents:
                addmemsegmentrecursive(m)

        #Entry point
        try:
            rootmemsegment=basefile.memorysegmentsbyname['main']
        except KeyError:
            raise  CompileError('No entry point found')

        addmemsegmentrecursive(rootmemsegment)
    
        Compiler.assignmemorysegments(memsegmentstoadd,rootmemsegment)


        Compiler.phase=2
        for file in includedfiles.values():
            file.compilephase2()

        for m in memsegmentstoadd:
            print(m)

        result=[None] * programsize
        for m in memsegmentstoadd:
            if len(m.content) != m.size:
                raise ValueError()
            for index,c in enumerate(m.content):
                addr = m.baseaddress+index
                if result[addr] is not None:
                    raise ValueError()
                result[addr]=c
        
        outputfile = open('output.txt','w')
        for index,c in enumerate(result):
            if c is not None:
                outputfile.write('{} {}\n'.format(index,c))


    def assignmemorysegments(memsegments,zerosegment=None):
        currentmemindex=0

        if zerosegment:
            zerosegment.baseaddress=currentmemindex
            currentmemindex+=zerosegment.size
            
            memsegments=[x for x in memsegments if x is not zerosegment]

        for m in memsegments:
            m.baseaddress=currentmemindex
            currentmemindex+=m.size

            if currentmemindex>=2**15:
                raise ValueError('Program is to big')



        
    def ms(value):
        if Compiler.phase==1:
            result = MemorySegment()
            result.size=1
            if type(value) is MemorySegment or type(value) is DependentConstant:
                result.dependents=[value]
            return result
        elif Compiler.phase==2:
            return MemorysegmentContent([value])

    

    def getglobalandinportedvariables(filenames):
        #TODO: implement imports

        imported={}

        return mergedicts(Compiler.getglobalvariables(),imported)

    def getglobalvariables():
        return Compiler.globalvariables


class FileCompiler(object):
    
    def __init__(self,filename):

        self.name = filename
        self.dependencies = []

        with open(filename+fileextension,'r') as f:
            self.lines = [self.trimcomments(x) for x in f.readlines()]    
        self.readimports()



    def compilephase1(self):

        self.globalvariables = Compiler.getglobalandinportedvariables(self.dependencies)
        self.localvariables = {}


        self.memorysegments=[]
        self.memorysegmentsbyname={}

        self.iteratelines()

        for k,v in self.localvariables.items():
            if type(v) is MemorySegment:
                v.sourcefile=self
                v.name=k
                self.memorysegments.append(v)
                self.memorysegmentsbyname[k]=v
        
    def compilephase2(self):
        #self.variabledeclarations = self.localvariables
        

        self.iteratelines()
          
    
    def iteratelines(self):
        context=None

        for i,line in enumerate(self.lines):
            
            self.linenumber=i+1

            if context != 'code':
                line=line.strip()

            if not line:
                continue


            if line.startswith('#import'):pass
            elif line.startswith('#code'):
                context='code'
                self.begincodesegment()
            elif line.startswith('#endcode'):
                context=None
                self.endcodesegment()
            elif line.startswith('#data'):      context='data'
            elif line.startswith('#enddata'):   context=None
            elif line.startswith('#def '):      self.dodefstatement(line.partition('#def ')[2])
            elif line.startswith('%'):
                context = 'program'
                self.beginprogramsegment(line.partition('%')[2])

            else:
                if context=='data':              self.datastatement(line)
                elif context=='code':            self.codestatement(line)
                elif context=='program':         self.programstatement(line)
                else:
                    raise Exception()

     
    def programstatement(self,line):

        tmp = line.split(' ')
        mnemonic = tmp[0].lower()
        args = [eval(x,self.globalvariables,self.localvariables) for x in tmp[1:]]
        
        for i,arg in enumerate(args):
            if type(arg) is MemorySegment:
                self.memblock.dependents.add(arg)
                args[i]=arg.baseaddress
            if type(arg) is DependentConstant:
                self.memblock.dependents|=arg.dependents
                args[i]=0

        syntax = Syntax.Query(mnemonic,args)
        if not syntax:
            raise CompileError('instruction not found')


        if Compiler.phase==1:
            self.memblock.size+=syntax.size
        elif Compiler.phase==2:
            self.memblock.content+=syntax.compile(args)

    
    def datastatement(self,line):
        self.dodefstatement(line)
            
    def beginprogramsegment(self,name):
        if Compiler.phase==1:
            self.memblock = MemorySegment()
            self.localvariables[name]=self.memblock
        elif Compiler.phase==2:
            self.memblock=self.memorysegmentsbyname[name]
        
    def dodefstatement(self,statement):
        exec(statement,self.globalvariables,self.localvariables)
        if Compiler.phase == 2:
            for k,v in self.localvariables.items():
                if type(v) is MemorysegmentContent:
                    self.memorysegmentsbyname[k].content=v.content
                    self.localvariables[k]=self.memorysegmentsbyname[k]
            





    #region TODO: codestatments
    def begincodesegment(self):
        pass

    def codestatement(self,line):
        print(self.linenumber,'code')



    def endcodesegment(self):
        pass

    #endregion
    


    def readimports(self):
        

        for line in self.lines:
            line = line.strip()
            if line.startswith('#import '):
                self.dependencies.append(line.partition('#import ')[0])
            elif line.startswith('#endimport'):
                break

    def trimcomments(self,line):
        if '//' in line:
            line= line.partition('//')[0]
        return line.strip('\n')



    #Get memory Segments
    def getmemorysegments(self):
        pass

     