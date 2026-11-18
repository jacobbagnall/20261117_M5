class calculatour:

    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.nirosh = 2.45
    
    def get_sum(self):
        return self.a + self.b
    
    def get_mins(self):
        return self.a - self.b
    
    def get_div(self):
        return self.a / self.b
    
    def get_muit(self):
        return self.a * self.b
    
    def nirosh_index(self):
        ans = (self.a + self.b)*self.nirosh + 100    

if __name__ == "__main__":
    myCalc = calculatour(a=5,b=6)

