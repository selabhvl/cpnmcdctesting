(* implementation of the test case specification for the TPC example *)

structure TPCTCSpec : TCSPEC = struct
	  
fun detection (Bind.Workers'Receive_CanCommit _)  = true
  | detection (Bind.Coordinator'Receive_Acknowledgements _) = true
  | detection (Bind.Workers'Receive_Decision _)  = true
  | detection _ = false;

exception obsExn;
fun observation (Bind.Workers'Receive_CanCommit (_,{w,vote}))  = [InEvent (w,vote)]
  | observation (Bind.Coordinator'Receive_Acknowledgements (_,{workers,decision}))  = [OutEvent (SDecision decision)]
  | observation (Bind.Workers'Receive_Decision (_,{w,decision})) = [OutEvent (WDecision (w,decision))]
  | observation _ = raise obsExn; 

fun format (InEvent (wrk(i),vote)) =
  "      <Vote>\n"^
  "        <WorkerID>"^(Int.toString i)^"</WorkerID>\n"^
  "        <VoteValue>"^(if vote = No then "1" else "0")^"</VoteValue>\n"^
  "      </Vote>\n"
  | format (OutEvent (WDecision (wrk(i),decision))) =
    "        <Decision>\n"^
    "          <WorkerID>"^(Int.toString i)^"</WorkerID>\n"^
    "          <DecisionValue>"^(if decision = abort then "1" else "0")^"</DecisionValue>\n"^
    "        </Decision>\n"
  | format (OutEvent (SDecision (decision))) =
    "        <FinalDecision>"^(if decision = abort then "1" else "0")^"</FinalDecision>\n";

fun sort_fn (InEvent _,OutEvent _) = true
  | sort_fn (InEvent (w1,_),InEvent (w2,_)) = Worker.lt(w1,w2)
  | sort_fn (OutEvent (WDecision (w1,_)),OutEvent (WDecision (w2,_))) = Worker.lt(w1,w2)
  | sort_fn (OutEvent (WDecision _),OutEvent (SDecision _)) = true
  | sort_fn (OutEvent (SDecision _),OutEvent (WDecision _)) = false
  | sort_fn (OutEvent (SDecision _),OutEvent (SDecision _)) = true
  | sort_fn (_,_) = false; 

fun normalise tce = sort sort_fn tce;

end;

(* setup test case generation for the TPC example *)
Config.setTCdetect(TPCTCSpec.detection);
Config.setTCobserve(TPCTCSpec.observation);
Config.setTCformat(TPCTCSpec.format);
Config.setTCnormal(TPCTCSpec.normalise);
