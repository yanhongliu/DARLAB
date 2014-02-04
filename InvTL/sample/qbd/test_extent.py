import qbdlib
class zog():
    def __init__(self):
        qbdlib.register(self)

class zog2():
    def __init__(self):
        qbdlib.register(self)

for i in range(10):
    zog()
print len(qbdlib.extent(zog))

for i in range(10):
    z=zog()
print len(qbdlib.extent(zog))
z=12
print len(qbdlib.extent(zog))

arr=[]
for i in range(10):
    arr.append(zog())
print len(qbdlib.extent(zog))

