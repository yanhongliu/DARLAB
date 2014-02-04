-module(ebay).
-export([test/0,ebayserver/3,client/2]).
   
ebayserver(Price,Winner,Bidders) ->
 receive
	 {bid,ITEM,FROM,PRICE} -> 
		 if 
		   PRICE>Price ->
             lists:map(fun(B) -> B!{price,ITEM,FROM,PRICE} end,Bidders),
		     ebayserver(PRICE,FROM,Bidders);
	       PRICE=<Price ->
			   ebayserver(Price,Winner,Bidders)
	     end;
	 {registerforprice,ITEM,FROM} -> 
		 FROM!{price,ITEM,Winner,Price},
		 ebayserver(Price,Winner,[FROM]++Bidders)
		 
 end.

client(Server,Maxprice) ->
 receive
    {price,ITEM,Winner,Price} -> 
		io:format("C<~w> winner ~w price ~w~n",[self(),Winner,Price]),
		S=self(),
	    if 
		  Winner/=S ->
			  if Price<Maxprice ->
					  Server!{bid,ITEM,S,Price+1},
				      client(Server,Maxprice);
				 Price>=Maxprice ->
				      client(Server,Maxprice)
		      end;
		  Winner==S ->
			  client(Server,Maxprice)
	    end
 end.

test() ->
  S = spawn(ebay,ebayserver,[0,self(),[]]),
  C1 = spawn(ebay,client,[S,21]),
  C2 = spawn(ebay,client,[S,30]),
  S!{registerforprice,0,C1},
  S!{registerforprice,0,C2},
  io:format("Done.~n",[]).
  

