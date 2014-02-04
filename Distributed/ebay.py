from candygram import *
import time
import collections

class ebayserver:
    def __init__(self):
        self.peers=set()
        self.price=0
        self.winner=self_()
        
    def launchthread(self,id):
        R = Receiver()
        R[str,Process,Any] = self.process, id, Message        
        R[str,Process,Any,Any] = self.process, id, Message        
        #R['register',Process,Any]=self.register, id, Message
        #R['bid',Process,Any,Any]=self.bid, id, Message
        for message in R:
          pass 

    #Candygram is broken
    def process(self,id,message):
        eval("self."+message[0])(id,message[1:])
    
    def register(self,id,message):
        FROM,ITEM=message
        print id, "recieved", message
        self.peers.add(FROM)
        FROM|("price","ITEM",self.winner,self.price)

    def bid(self,id,message):
        FROM,ITEM,PRICE=message
        print id, "recieved", message
        if PRICE>self.price:
            self.price=PRICE
            self.winner=FROM
            for p in self.peers:
                p |("price","ITEM",self.winner,self.price)

class Client:
    def __init__(self,server,maxprice):
        self.server=server
        self.maxprice=maxprice
    def launchthread(self,id):
        R = Receiver()
        R[str,Any,Process,Any]=self.process, id, Message
        self.server | ("register",self_(),"ITEM")
        for message in R:
          pass 

    def process(self,id,message):
        eval("self."+message[0])(id,message[1:])
    
    def price(self,id,message):
        item,winner,price = message
        print id, "recieved", message
        if winner!=self_() and price<self.maxprice:
           self.server | ("bid",self_(),"ITEM",price+1)




def launch(R,name):
    P = spawn(R.launchthread,name)
    R.proc = P
    print name, P
    return R
    
server = launch(ebayserver(),"S")
Client(1,2)
c1     = launch(Client(server.proc,20),"C1")
c2     = launch(Client(server.proc,30),"C2")

time.sleep(1)
