from reach import Reach

def rand_graph(size,ratio):
    E={}
    S2=range(size)
    #print S2
    for i in range(size):
        E[i] = set(random.sample(S2,int(size*ratio)))
        #E[i].add(i)
    #for i in range(size-1): E[i].add(i+1)

    print size*ratio*size
    return E

def test():
    r = Reach() 
    E=rand_graph(100,.01)
    r.buildGraph(E)
    print len(r.Reach(1))

test()
