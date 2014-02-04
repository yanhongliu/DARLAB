-module(lamport).
-export([driver/0,test/0]).

%Algorithm
%
%Requesting process
%
%   1. Enters its request in its own queue.
%   2. Sends a request to every node.
%   3. Wait for replies from all other nodes.
%   4. If own request is at the head of the queue and all replies have been received, enter critical section.
%   5. Upon exiting the critical section, send a release message to every process.
%
%Other processes
%
%   1. After receiving a request, send a reply and enter the request in the request queue
%   2. After receiving release message, remove the corresponding request from the request queue.
%   3. If own request is at the head of the queue and all replies have been received, enter critical section.


%Erlang has no built-in max function
max(E1,E2) ->
 T1 = E1, 
 T2 = E2, 
 if 
   T1 > T2 -> 
	    T1 ; 
   true -> T2 
 end.

%Send Msg to all peers
sendAll(Msg,[]) -> [];
sendAll(Msg,[Peer|Rest]) ->
  Peer!Msg,
  sendAll(Msg,Rest).

%Request critical section:
% Add self to queue, then send messages, then return new QUEUE
requestCrit(Plist,Requestq,CT) ->
  NQ=queue:in({request,CT,self()},Requestq),
  sendAll({request,CT,self()},sets:to_list(Plist)),
  NQ.

%Release critical sectino
% Send release to all peers, remove self from queue, return new queue
releaseCrit(Plist,Requestq,CT) ->
  sendAll({release,CT,self()},sets:to_list(Plist)),
  {_,NQ} = queue:out(Requestq),
  NQ.

%Execute critical section code
execCrit(Plist,Requestq,F,CT) ->
  io:format("CS START: ~w~n",[self()]),
  F(),
  io:format("CS END: ~w~n",[self()]),
  RC=releaseCrit(Plist,Requestq,CT),
          %This randomly fires mutex requests
		  R=random:uniform(500),
		  io:format("~w~n",[R]),
		  if R==47 -> self()!{acquirelock};
             true -> [] 
		  end,
  RC.

%Check whether we can execute critical section code.
%Also restarts the listener
checkCriticalSection(Plist,Requestq,Replies,FUN,CT) ->
  S=self(), 
  case queue:is_empty(Requestq) of
    true ->
      listen(Plist,Requestq,Replies,FUN,CT);
    false ->
      {R,T,F} = queue:head(Requestq),
      if 
        F==S -> %If we are at the head of the queue
          FL = sets:from_list([From || {Time,From} <- sets:to_list(Replies), Time >=T]),
		  %FL is the set of peers that replied to us after our request
		  case FL == Plist of 
	        true -> %if all peers replied, enter critical section, and
				    %increment logical time from the release
  		      NQ=execCrit(Plist,Requestq,FUN,CT+1),
		      listen(Plist,NQ,Replies,FUN,CT+1);
  	        false -> 
	  	      listen(Plist,Requestq,Replies,FUN,CT)
	      end;
        F/=S ->
	      listen(Plist,Requestq,Replies,FUN,CT)
      end
end.

%Main listen loop
listen(Plist,Requestq,Replies,FUN,CT) ->
 receive
         {request,TIME,FROM} -> 
                io:format("<~w> request time:~w from:~w~n",[self(),TIME,FROM]),				
                FROM!{reply,max(TIME+1,CT),self()},
                listen(Plist,queue:in({request,TIME,FROM},Requestq),Replies,FUN,max(TIME+1,CT));
         {release,TIME,FROM} -> 
                io:format("<~w> release time:~w from:~w~n",[self(),TIME,FROM]),
                NQ = queue:filter(fun ({R,T,F}) -> F/=FROM end, Requestq),
                checkCriticalSection(Plist,NQ,Replies, FUN, max(TIME+1,CT));
         {reply,TIME,FROM} ->
                io:format("<~w> reply time:~w from:~w~n",[self(),TIME,FROM]),
                NR = sets:add_element({TIME,FROM},Replies),                
				checkCriticalSection(Plist,Requestq,NR, FUN, max(TIME+1,CT));
         {acquirelock} ->
                io:format("<~w> Acquiring mutex...~n",[self()]),
                NQ = requestCrit(Plist,Requestq,CT+1),
                listen(Plist,NQ,Replies,FUN,CT+1);
         {quit} ->
                io:format("<~w> quitting~n",[self()])
 end.

%The driver for each process
driver() ->
  io:format("Starting driver.~n",[]),
  receive 
         {start,PLIST,FUN} ->
            io:format("Starting listener~n",[]),
			listen(sets:del_element(self(),PLIST),queue:new(),sets:new(),FUN,0);
         {stop} ->
            self()!{quit},
            io:format("Stopping driver~n",[])

  end.   

%The local thread that launches the process
test() ->
  P1 = spawn(lamport,driver,[]),
  P2 = spawn(lamport,driver,[]),
  P3 = spawn(lamport,driver,[]),
  P4 = spawn(lamport,driver,[]),
  L = sets:from_list([P1,P2,P3,P4]),
  F = fun() -> [] end,
  P1!{start,L,F},
  P2!{start,L,F},
  P3!{start,L,F},
  P4!{start,L,F},
  P3!{acquirelock},
  P1!{acquirelock},
  P2!{acquirelock},
  P4!{acquirelock},
  io:format("Done.~n",[]).

