from pathlib import Path
from datetime import datetime

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
    
      

    
if __name__ == "__main__":
    myCalc = calculatour(a=247,b=12)

    out = Path("/data/hello.txt")
    out.parent.mkdir(parents=True, exist_ok=True)

    line = f"{datetime.now()} Divide: {myCalc.get_div()}"
    print(line)

    with out.open("a") as f:
        f.write(line + "\n")


