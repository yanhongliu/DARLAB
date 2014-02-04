from candygram import *
import time
import collections

class Proc:    
    def __init__(self):
        self.requests = collections.deque() #The queue
        self.replies  = set()
        self.peers    = set()
        self.time     = 0

    #Send msg to all peers
    def sendAll(self, msg):
        for p in self.peers:
            if p!=self_():
              p | msg

    #Request critical section
    # Increment time, add self to queue, then send messages 
    def requestCrit(self):
        self.time+=1
        self.requests.appendleft((self.time,self_()))
        self.sendAll(('request',self.time,self_()))

    #Release critical sectino
    # Increment time, send release to all peers, remove self from queue
    def releaseCrit(self):
        self.time+=1
        self.sendAll(('release',self.time,self_()))
        self.requests.pop()

    #Execute the critical section body
    def execCrit(self):
        print self_(), "entered critical section" 
        print self_(), "left critical section" 
        self.releaseCrit()
    
    #Launcher for the candygram thread
    def launchthread(self,id):
        R = Receiver()
        R["acquirelock"]=self.acquirelock, id
        R[str,int,Process]=self.process, id, Message
        for message in R:
          pass 

    #This is here because in launchthread, 
    #       R["request",int,Process]=self.request, id, Message
    #       R["reply",int,Process]=self.reply, id, Message
    #does not work for some reason, even though it should.
    def process(self,id,message):
        print id, "recieved", message
        #Giant hack.
        eval("self."+message[0])(id,message[1:])
    
    #Check whether we can execute critical code
    def checkCriticalSection(self):
        if self.requests:
            T,F=self.requests[-1] #Get the front of the queue
            if F==self_():
                FL=set([From for Time,From in self.replies if Time>=T])
                if len(FL)+1==len(self.peers): #If the sets are the same (The
                                               #+1 is there because self.peers contains self.)
                    self.execCrit()
    
    def acquirelock(self,id):
        self.requestCrit()

    def request(self,id,message):
        time,proc = message
        self.time=max(self.time,time+1)
        proc | ('reply',self.time,self_())
        self.requests.appendleft( message )

    def release(self,id,message):
        time,proc = message
        self.time=max(self.time,time+1)
        self.requests = collections.deque([(T,F) for (T,F) in self.requests if F!=proc])
        self.checkCriticalSection()
    
    def reply(self,id,message):
        time,proc = message
        self.time=max(self.time,time+1)
        self.replies.add(message)
        self.checkCriticalSection()


#Creates the process, sets up .proc
def launch(name):
    R = Proc()
    P = spawn(R.launchthread,name)
    R.proc = P
    print name, P
    return R

P1=launch("P1")
P2=launch("P2")
P3=launch("P3")
RL=[P1,P2,P3]
for r in RL:
    r.peers=[p.proc for p in RL]

P1.proc | 'acquirelock'
P3.proc | 'acquirelock'
P3.proc | 'acquirelock'
P3.proc | 'acquirelock'
P3.proc | 'acquirelock'
P2.proc | 'acquirelock'
P1.proc | 'acquirelock'

#Needed to not terminate this thread
time.sleep(1)

