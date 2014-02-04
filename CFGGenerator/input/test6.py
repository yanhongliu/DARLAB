class C:
    def __init__(self):
        self.R=set()
        self.S=set()
    def F(self):
        pass
    def setA(self,x):
        self.R.add(x)
        self.F()
    def setB(self,y):
        self.S.add(y)
        pass


c=C()
c.setA(1)
c.setB(2)
t=3
