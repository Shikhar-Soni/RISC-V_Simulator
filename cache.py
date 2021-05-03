import math
from helperFunctions import *

def make_length(data, length):
    data = "0"*length+data
    return data[-length:]
class Cache:

    def __init__(self, cache_size, block_size, ways):
        self.initialise(cache_size, block_size, ways)
        
    def initialise(self, cache_size, block_size, ways):
        self.cache_size = cache_size
        self.block_size = block_size
        self.ways = ways #number of ways
        self._cache = [] #list for now
        self._LRU = []
        self.index = int(math.log2(cache_size/block_size)) - int(math.log2(ways)) #index bits
        self.BO = int(math.log2(block_size)) #block offset bits
        self.tag = 32 - self.index - self.BO #tage bits
        print("index: ", self.index, " BO :", self.BO, " tag: ", self.tag)
        self.miss = 0
        self.hits = 0
        self.total_accesses = 0
        self.createCache()
        self.initialiseLRU()

    def address_break(self, address): #takes the hex string
        #should return binary, returns decimal for now
        address = hexToBin(address)
        address = make_length(address, 32)
        print("len", len(address))
        tag = address[:self.tag]
        index = address[self.tag:self.tag+self.index]
        BO = address[-self.BO:]
        print("tag :", tag, " index :", index, " BO :" , BO)
        return tag, index, BO

    def createCache(self):
        #modify the dict for easy access
        """
            let there be a cache of 8 byte size
            and a block is of size 1 byte
            there will be 8 blocks i.e., 8 dicts, one for each block
            cache = [{}, {}, {}, {}]
        """
        
        for i in range(2**self.index):
            self._cache.append({}) #every list
     #every dict will be a block, and there will be as many dict as ways
     

        
    def initialiseLRU(self):
        # [1/0, state, tag]
        for ind in range(2**self.index):
            self._LRU.append([])
            for blocks in range(self.ways):
                self._LRU[ind].append([0,0,0])
                
    def checkCache(self, index, tag):

        if tag in self._cache[index]:
            return True
        return False
        
    def updateLRU(self, tag, index):

        for i in range(self.ways):
            if self._LRU[index][i][0] == 1 and self._LRU[index][i][2] == tag:
                self._LRU[index][i][1] = self.ways
                for j in range(self.ways):
                    self._LRU[index][j][1] = max(self._LRU[index][j][1]-1, 0)
                return -1
            
        for i in range(self.ways):
            if self._LRU[index][i][0] == 0:
                self._LRU[index][i][0] = 1
                self._LRU[index][i][1] = self.ways
                self._LRU[index][i][2] = tag
                for j in range(self.ways):
                    self._LRU[index][j][1] = max(self._LRU[index][j][1]-1, 0)
                return -1
            
        minS = 1e9
        victim = 0
        for i in range(self.ways):
            if(minS > self._LRU[index][i][1]):
                minS = self._LRU[index][i][1]
                victim = i
                  
        self._LRU[index][victim][0] = 1
        self._LRU[index][victim][1] = self.ways
        oldTag = self._LRU[index][victim][2]
        self._LRU[index][victim][2] = tag
        for j in range(self.ways):
            self._LRU[index][j][1] = max(self._LRU[index][j][1]-1, 0)
        return (0, oldTag)

    def write(self, address, memory_obj, data, size, control):
        self.total_accesses += 1
        tag, index, BO = self.address_break(address)
        oldindex=index
        index = int(index, 2)
        BO = int(BO, 2)
        isVictim = self.updateLRU(tag, index)
        # print(tag,oldindex,BO,int(tag,2)+index+BO==32)
        # print(len(tag),len(oldindex),self.BO)
        address2 = tag+oldindex+"0"*self.BO
        print(tag,oldindex,BO,address2)
        address2 = binToHex(address2)
        print(address2)
        memory_obj.store_block( address2, data, 2**size, control)
        
        if(self.checkCache(index, tag)):
            self.hit+=1
            self._cache[index][tag] = list(self._cache[index][tag])
            self._cache[index][tag][2*BO:2*BO+(2**(size+1))] = data
            self._cache[index][tag] = "".join(self._cache[index][tag])

            
        else:
            self.miss+=1
            address2 = tag+oldindex+"0"*self.BO
            address2 = binToHex(address2)
            data2 = memory_obj.load_block( address2, self.block_size, control)
            if(isVictim == -1):
                self._cache[index][tag] = data2
            else:
                del self._cache[index][isVictim[1]]
                self._cache[index][tag] = data2
        
        
        
    def read(self, address, memory_obj, size, control):
        self.total_accesses += 1
        tag, index, BO = self.address_break(address)
        oldindex = index
        index = int(index, 2)
        BO = int(BO, 2)
        isVictim = self.updateLRU(tag, index)
        
        if(self.checkCache(index, tag)):
            self.hit += 1
            return self._cache[index][tag][2*BO:2*BO+(2**(size+1))]
        else:
            self.miss += 1
            address2 = tag+oldindex+"0"*self.BO
            print("address :", address2)
            address2 = binToHex(address2)
            data = memory_obj.load_block(address2, self.block_size, control)

            if(isVictim == -1):
                self._cache[index][tag] = data  
            else:
                del self._cache[index][isVictim[1]]
                self._cache[index][tag] = data
            self.printall()
            return self._cache[index][tag][2*BO:2*BO+(2**(size+1))]
            

    def printall(self):
        print(self._cache)
        print(self._LRU)