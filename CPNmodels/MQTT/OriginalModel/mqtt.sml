
fun getRoles(c : Client) = flatten(List.map(fn (c' : Client, listroles : roles) => listroles) (List.filter (fn (c' : Client,listroles : roles) => c=c') (!roleconfig)));

fun isSubscriber (cs : ClientxState) = 
let
val cstate = #2 cs
val roles = #roles cstate
val subrole = subscriber : role
val exists = List.exists (fn (subrole' : role) => subrole' = subrole) roles;
in
exists
end;

fun isPublisher (cs : ClientxState) = 
let
val cstate = #2 cs
val roles = #roles cstate
val pubrole = publisher : role
val exists = List.exists (fn (pubrole' : role) => pubrole' = pubrole) roles;
in
exists
end;

fun setClientState ((c,{topics,state,pid,roles}),DISC) = 
  (c, {topics = [], state = DISC, pid = pid, roles = getRoles(c)})
  | setClientState ((c,{topics,state,pid,roles}),newstate) = 
  (c, {topics = topics, state = newstate, pid = pid, roles = getRoles(c)});

fun isSubscribed (t,(c,{topics,state,pid,roles})) = mem (List.map (fn (t,qos) => t) topics) t;

fun notSubscribed (t,cs) = not (isSubscribed (t,cs));


fun getMsgs inmsgs (c,state) =
  let
      val inmsgclient = case (List.find (fn (c',inmsgs) => c = c') inmsgs) of
			    SOME (_,inmsg) => inmsg
			  | NONE => [] 
  in
      inmsgclient
  end;
      
fun hasMsg cs (inmsgs,msgfn) =
  let
      val clientinmsgs = getMsgs inmsgs cs
  in
      case clientinmsgs of
	  [] => false
	| (x::xs) => msgfn x
  end

exception getMsgExn;
fun getMsg (cs,inmsgs) =
  let
      val clientinmsgs = getMsgs inmsgs cs
  in
      case clientinmsgs of
	 (msg::_) => msg
	| _ => raise getMsgExn 
  end
  
fun hasCONNACK (cs,inmsgs) = hasMsg cs (inmsgs,(fn msg => msg = CONNACK));

fun hasSUBACK (cs,inmsgs) = hasMsg cs (inmsgs,(fn SUBACK _ => true | _ => false));

fun hasUNSUBACK (cs,inmsgs) = hasMsg cs (inmsgs,(fn UNSUBACK _ => true | _ => false));

fun hasPUBLISH qos (cs,inmsgs) = hasMsg cs (inmsgs,(fn (PUBLISH (t,qos',pid)) => qos = qos' | _ => false));

fun hasPUBREL (cs,inmsgs) = hasMsg cs (inmsgs,(fn (PUBREL _) => true | _ => false));

fun hasPUBREC (cs,inmsgs,(t,pid)) = hasMsg cs (inmsgs,(fn (PUBREC (t',pid')) => pid = pid' andalso t = t'  | _ => false));

fun hasPUBCOMP (cs,inmsgs) = hasMsg cs (inmsgs,(fn (PUBCOMP _) => true | _ => false));

fun rmPid (listpids,SUBACK(t,qos,pid)) = rm pid listpids
  | rmPid (listpids,UNSUBACK(t,pid)) = rm pid listpids
  | rmPid (listpids,PUBACK(t,pid)) = rm pid listpids 
  | rmPid (listpids,_) = listpids; 

(* TODO: fix use of fake client state below *)
fun hasPUBACK (c,inmsgs) = hasMsg (c,{state=CON,topics=[],pid=0, roles = getRoles(c)}) (inmsgs,(fn PUBACK _ => true | _ => false));


fun clientSubTopic (cs : ClientxState,SUBACK(t, qos,pid), listpids : ListPID)=
  let
      val clist = #2 cs
      val c = #1 cs
      val topicsList = #topics clist
	  val roles = #roles clist
      val updatedList = removeTopic (topicsList, t) (* ERROR ? or due to potential update?*)
  in
      if (mem listpids pid)
      then
	  case #state clist of
	      DISC => (c, {topics = topicsList, state = DISC, pid = #pid clist, roles = roles})
	    | WAIT => (c, {topics = topicsList, state = WAIT,  pid = #pid clist, roles = roles})
	    | CON => (c, {topics = sorttopic (ins updatedList (t,qos)), state = #state clist, pid = #pid clist, roles = roles}) (* LMK *)
      else
	  case #state clist of
	      DISC => (c, {topics = topicsList, state = DISC, pid = #pid clist, roles = roles})
	    | WAIT => (c, {topics = topicsList, state = WAIT,  pid = #pid clist, roles = roles})
	    | CON => (c, {topics = topicsList, state = #state clist, pid = #pid clist, roles = roles})
  end
  | clientSubTopic (cs,_,_) = cs;

fun clientUnsubscribe(cs : ClientxState,UNSUBACK(t,pid), listpids : ListPID) =
  let
      val clist = #2 cs
      val c = #1 cs
      val topicsList = #topics clist
	  val roles = #roles clist
      val updatedList = removeTopic (topicsList, t)
  in
      if (mem listpids pid)
      then
	  case #state clist of
	      DISC => (c, {topics = topicsList, state = DISC, pid = #pid clist, roles = roles})
	    | WAIT => (c, {topics = topicsList, state = WAIT, pid = #pid clist, roles = roles}) (* LMK: is this possible ? *)
	    | CON => (c, {topics = updatedList, state = #state clist, pid = #pid clist, roles = roles})
      else
	  case #state clist of
	      DISC => (c, {topics = topicsList, state = DISC, pid = #pid clist, roles = roles})
	    | WAIT => (c, {topics = topicsList, state = WAIT, pid = #pid clist, roles = roles})
	    | CON => (c, {topics = topicsList, state = #state clist, pid = #pid clist, roles = roles})
  end
      
(* safe version of tail operation that will not raise an exception in case of empty list *)
fun stl [] = []
  | stl xs = List.tl xs;

fun recvMsg ((c,_),inmsgs) =
  List.map
      (fn (c',cinmsg) =>
	  if (c = c')
	  then (c,stl cinmsg)
	  else (c',cinmsg))  
      inmsgs;

fun precvMsg (c,inmsgs) = recvMsg ((c,{state=CON,topics=[],pid=0, roles = getRoles(c)}),inmsgs);

fun pgetMsg (c,inmsgs) = getMsg ((c,{state=CON,topics=[],pid=0, roles = getRoles(c)}),inmsgs);

fun rmPidT (ps,msg) =
  List.map
      (fn pid => (pid,topic(1)))
  (rmPid ((List.map (fn (pid,_) => pid) ps),msg))

fun sendPUBACK (c,inmsgs) =
  let
      val msg = pgetMsg (c,inmsgs)
  in
      case msg of
	  PUBLISH (t,qos,pid) => [(c,PUBACK(t,pid))]
	| _ => []
  end;

fun sendPUBREC (c,inmsgs) =
  let
      val msg = pgetMsg (c,inmsgs)
  in
      case msg of
	  PUBLISH (t,qos,pid) => [(c,PUBREC(t,pid))]
	| _ => []
  end;

fun sendPUBREL (c,inmsgs) =
  let
      val msg = pgetMsg (c,inmsgs)
  in
      case msg of
	  PUBREC (t,pid) => [(c,(t,pid))]
	| _ => []
  end;

fun getPublish (c,inmsgs) =
  let
      val msg = pgetMsg (c,inmsgs)
  in
      case msg of
	  PUBLISH (t,qos,pid) => [(pid,t)]
	| _ => []
  end;
  
fun getPubComp (c,inmsgs) =
  let
      val msg = pgetMsg (c,inmsgs)
  in
      case msg of
	  PUBCOMP (t,pid) => [(t,pid)]
	| _ => []
  end;

exception getPUBCOMPExn;

fun getPUBCOMP (c,inmsgs) =
  let
      val msg = pgetMsg (c,inmsgs)
  in
      case msg of
	  PUBCOMP (t,pid) => (pid,t)
	| _ => raise getPUBCOMPExn
  end;

exception getPUBRELExn  
fun getPUBREL (c,inmsgs) =
  let
      val msg = pgetMsg (c,inmsgs)
  in
      case msg of
	  PUBREL (t,pid) => (pid,t)
	| _ => raise getPUBRELExn
  end;  

fun pubPUBCOMP (c,inmsgs,pidtopics) =
  (let
      val (pid,t) = getPUBCOMP(c,inmsgs)
  in
      mem pidtopics (pid,t) 
  end
       handle _ => false)
      
fun sendPUBCOMP (c,inmsgs) =
  let
      val msg = pgetMsg (c,inmsgs)
  in
      case msg of
	  PUBREL (t,pid) => [(c,PUBCOMP(t,pid))]
	| _ => []
  end;

(* for sending in the client side *)
fun sendMsg msgs ((c,_),msg) = msgs^^[(c,msg)];

(* for sending one message in the broker side *)
fun bsendMsg (msgs,(c,msg)) =
  List.map
      (fn (c',cinmsg) =>
	  if c = c' then (c,cinmsg^^[msg]) else (c',cinmsg))
      msgs;

(* for sendimg multiple messages in the broker side *)
fun bsendMsgs (msgs,smsgs) = List.foldr (fn ((c,msg),msgs) => bsendMsg (msgs,(c,msg))) msgs smsgs;

fun isClientConnected (clstates,c) = List.exists (fn (c',_) => c = c') clstates;

fun filterTopics (topics, t) = List.filter(fn(t',_) => t = t') topics;


fun sortClients clstates = 
	sort (
		fn ((client(i), _), (client(j), _)) => i<j
	)
	clstates;
	
fun sortTopics topics = 
sort (
	fn ((topic(i), _), (topic(j), _)) => i<j
)
topics;	


fun	flatten nil = nil

|	flatten (h::t) = h ^^ flatten t;


fun brokerSubscribeUpdate (clstates,(c,t,qos)) =
	  (List.map
	       (fn (c',(cstate as {topics,state,pid,roles}: ClientState)) =>
		   if (c'=c)
		   then
		       (c',{state=state,
			     pid = pid,
			     topics =
			     if (List.exists (fn (t',_) => t=t') topics)
				    then sortTopics(List.map
					     (fn (t',qos') =>
						 if t=t' then (t,qos) else (t',qos'))
					     topics)
			     else sortTopics((t,qos)::topics),
		       roles = roles
			   })
		   else (c',cstate))
	       clstates);

fun brokerUnsubscribeUpdate (clstates,(c,t)) =
	(List.map
	   (fn (c',(cstate as {topics,state,pid,roles}: ClientState)) =>
			if (c'=c)
			then
			   (c',{state=state,
				 pid = pid,
				 topics =
				 List.filter (fn (t',qos') => t<>t') topics,
				 roles = roles
			   })
			else 
				(c',cstate)
	   )
	clstates
   )

fun brokerDisconnectUpdate (clstates, c) =
	(List.filter
	   (fn (c',_) =>
			(c'<>c)
	   )
	clstates
	);		    
		   

fun filtermap pred mapfn xs =
  List.map
      mapfn ((List.filter pred xs));

fun filtermap' pred mapfn xs =
  List.foldr (fn (x,xs) => if (pred x)
			   then (mapfn x)::xs
			   else xs) [] xs;
      
fun getSubscribed (t:Topic) (clstates : ClientsxState) =
  filtermap
      (fn (c, (cstate as {topics,state,pid,roles} : ClientState)) =>
	  List.exists (fn (t',_) => t = t') topics)
      (fn (c, (cstate as {topics,state,pid,roles} : ClientState)) => (c,pid))
      clstates;

fun assignBPids (oldclientspids: ClientsxPID) (clspid: ClientsxPID) =	  
	 List.filter (fn (c, bpid) => (List.exists( fn(c', _) => c = c' ) oldclientspids)) clspid
	  
	  
	  
fun filterForDispatching(clstates : ListClientxState, t : Topic)=
  List.map
      (fn (c, (cstate as {topics,state,pid,roles} : ClientState)) =>
	  (c, #2 (List.hd (List.filter (fn (t',qos) => t = t') topics))))
      (List.filter
	   (fn (c, (cstate as {topics,state,pid,roles} : ClientState)) =>
	       List.exists (fn (t',_) => t = t') topics)
	   clstates);

	   
	   
fun createPublishQoS1 listcxlptq =
  List.concat (
      List.map 
	  (fn (c,xs) => List.map (fn (pid,t,qos) => (c,PUBLISH(t,qos,pid))) xs)
	  (List.map
	       (fn (c,xs) => (c,List.filter (fn (pid,t,qos') => qos' = QoS(1)) xs))
	       listcxlptq)
	  );

	  
fun QoSmin (QoS(i),QoS(j)) = QoS(Int.min(i,j));

fun brokerDispatchPublishQos0 (t,subclspid) =
  (List.map (fn (c,bpid) => (c, PUBLISH(t,QoS(0),bpid))) subclspid);
  
fun brokerDispatchPublishQos1 (t, subclspid, c : Client, pid : PID) =
((c, PUBACK(t,pid)))::(List.map (fn (c,bpid) => (c, PUBLISH(t,QoS(1),bpid))) subclspid);

fun brokerDispatchPublishQos2 (t, subclspid, c : Client, pid : PID) =
((c, PUBCOMP(t,pid)))::(List.map (fn (c,bpid) => (c, PUBLISH(t,QoS(2),bpid))) subclspid);

fun incPIDs (subclspid,clspid) =
  List.map
      (fn (c,pid) => if (List.exists (fn (c',_) => c' = c) subclspid)
		     then (c,pid+1)
		     else (c,pid))
      clspid;

	  

exception getbpidException;
fun getbpid (c, subclspid : ClientsxPID) =
	let 
	val bpid = case (List.find (fn (c', pid : PID) => c = c') subclspid) of 
			SOME (_,pid) => pid
			| NONE => raise getbpidException 
	in
		bpid
end;


fun brokerCreateACKWaiting (t : Topic ,clstates : ClientsxState, listcxlptq : ListClientxListPIDxTopicxQoS, subclspid : ClientsxPID) =
List.map(
			fn (c: Client, listpidsxtopicsxqos : ListPIDxTopicxQoS) =>
			if (List.exists ( fn (c',_) => c' = c) subclspid)
			then
				(c, listpidsxtopicsxqos^^[(getbpid(c,subclspid),t, QoS(1))])
			else
				(c, listpidsxtopicsxqos)
		)listcxlptq


fun brokerCreateACKWaiting2 (t : Topic ,clstates : ClientsxState, listcxlptq : ListClientxListPIDxTopicxQoS, subclspid : ClientsxPID) =
List.map(
			fn (c: Client, listpidsxtopicsxqos : ListPIDxTopicxQoS) =>
			if (List.exists ( fn (c',_) => c' = c) subclspid)
			then
				(c, listpidsxtopicsxqos^^[(getbpid(c,subclspid),t, QoS(2))])
			else
				(c, listpidsxtopicsxqos)
		)listcxlptq	

(*
fun brokerDispatchPublishQos0 (bpid : PID, clstates : ListClientxState, t : Topic , qos : QoS) =
  (List.map
			     (fn (c',qos') => (c', PUBLISH(t,QoS(0),bpid)))
			     (filterForDispatching (clstates,t)));

				 
				 
fun brokerDispatchPublishQos1 (bpid : PID, clstates : ListClientxState, c : Client, t : Topic , pid : PID) =
  ((c, PUBACK(t,pid)))::(List.map
			     (fn (c',qos') => (c', PUBLISH(t,QoSmin(QoS(1),qos'),bpid)))
			     (filterForDispatching (clstates,t)));

		    
fun brokerDispatchPublishQos2 (bpid : PID, clstates : ListClientxState, c : Client, t : Topic, pid : PID) =
	
	  ((c, PUBCOMP(t,pid)))::(List.map
			     (fn (c',qos') => (c', PUBLISH(t,QoSmin(QoS(2),qos'),bpid)))
			     (filterForDispatching (clstates,t)));

*)	
fun brokerUpdateACKWaiting (c: Client, pid : PID, listcxlptq : ListClientxListPIDxTopicxQoS)=

	(List.map(
		(fn (c', listpidsxtopicsxqos) =>
			if (c = c')
			then
			(c',(List.filter(
				(fn (pid', t',_) =>
					(pid<>pid')
				)
			)
			listpidsxtopicsxqos
			))
			else
			(c', listpidsxtopicsxqos)
		)
	)	
	listcxlptq		
	);	

	
fun filterClientStates(clstates : ListClientxState, t : Topic)=
  List.map
      (fn (c, (cstate as {topics,state,pid,roles} : ClientState)) =>
		(c, #2 (List.hd (List.filter (fn (t',qos') => (t = t' andalso (qos' <> QoS(0)))) topics)))
		)
	  
      (List.filter
	   (fn (c, (cstate as {topics,state,pid,roles} : ClientState)) =>
	       List.exists (fn (t',qos') => (t = t' andalso qos' <> QoS(0))) topics)
	   clstates);	

	   


fun brokerAddACKSecondStep (c : Client, bpid : PID, t : Topic, listcxlptq2 : ListClientxListPIDxTopicxQoS)=
(	
	List.map
	(
		(fn (c', listpidsxtopicsxqos' : ListPIDxTopicxQoS) =>
			if (c = c')
			then
				(c', listpidsxtopicsxqos'^^[(bpid,t,QoS(2))])
			else
				(c', listpidsxtopicsxqos')
		)
	)listcxlptq2
);

fun connectClient(clstates,c) =  sortClients (clstates^^[(c, {topics = [],state = CON,pid=0, roles = getRoles(c)})])



(*
val cli = client(2);
val top = topic(1);
val listi = [(client(1),[]),(client(2),[])] : ListClientxListPIDxTopicxQoS;

val clstatess = [
(client(1),{topics=[(topic(1),QoS(0))],state=CON,pid=0}),
(client(2),{topics=[(topic(1),QoS(2))],state=CON,pid=0})];
filterClientStates (clstatess, top);
brokerCreateACKWaiting2 (cli, 1, clstatess, top, listi);
*)
