from collections import defaultdict

class Memory:

    def __init__(self):
        self.__memory = defaultdict(lambda:"00")    #only relevant data stored

    def load_byte(self, address):
        if address in self.__memory.keys():
            return self.__memory[address]
        else:
            return "00"

    def load_word(self, address):
        address_in_dec = int(address, 16)
        data = ""
        for i in reversed(range(4)):
            address_in_hex ="0"*8+hex(address_in_dec + i)[2:]
            address_in_hex = address_in_hex[-8:]
            data = data + self.load_byte(address_in_hex)
        return data

    def store_byte(self, address, data):
        self.__memory[address] = data

    def store_word(self, address, data):
        address_in_dec = int(address, 16)
        for i in range(4):
            address_in_hex = "0"*8+hex(address_in_dec+i)[2:]
            address_in_hex = address_in_hex[-8:]
            self.store_word(address_in_hex,data[6-2*i:8-2*i])

#mem = Memory()
#mem.store_byte("00000000","0A")
#print(mem.load_word("00000000"))
