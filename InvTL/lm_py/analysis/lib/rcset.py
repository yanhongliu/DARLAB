class rcset:
    def __init__(self):
        self.next = None
        self.last = self

    def __setitem__(self, k,value):
        n=self        
        while n.next is not None:
            if n.value==value:
                n.key=k
            n = n.next
        if n.next==None:
            n = self.last
            n.value = value
            n.key=k
            n.next = self.__class__()
            self.last = n.next

    def __getitem__(self,key):
        n=self        
        while n.next is not None:
            if n.value==value:
                return n.key
            n = n.next

    def __delitem__(self, key):
        pass

    def __len__(self):
        i = 0
        n = self
        while n.next is not None:
            n = n.next
            i += 1
        return i
    def add(self,k):
        pass
    def remove(self,k):
        pass
    def __true__(self):
        return self.__len__() != 0
    def __contains__(self,a):
        return True
    def __notcontains__(self,a):
        return False
    
