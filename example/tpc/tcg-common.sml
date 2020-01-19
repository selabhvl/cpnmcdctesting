
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

Config.setTCformat(format);
Config.setTCnormal(normalise);

(* logging and output *)
Config.setModelDir (mbtcpnlibpath^"examples/tpc/");
Config.setOutputDir ((Config.getModelDir())^"output/");

(* configuration and test case naming *)
Config.setConfigNaming (fn () => "tpctests-"^(Int.toString W));
Config.setTCNaming(fn i => "CaseID=\""^(Int.toString i)^"\" NumOfWorker=\""^(Int.toString W)^"\"");

val configs2 = [SS,(SIM 5),(SIM 10)]

val configs3 = [SS,(SIM 10),(SIM 20)]
		   
val configs4 = [SS,(SIM 50),(SIM 100)]

val configs5 = [SS,(SIM 100),(SIM 200)]

val configs10 = [(SIM 5000)(*,(SIM 10000)*)]

val configs15 = [(*(SIM 10000),*)(SIM 20000)]		   
