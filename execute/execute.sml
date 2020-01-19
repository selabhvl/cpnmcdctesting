structure Execute (* : TCGEN *) =
struct

(* simulation-based test case generation *)

fun tcscount tcs = (if (Config.getTestcaseevent ())
		    then   List.length (remdupl (List.concat tcs))
		    else (List.length tcs));

(* List.foldr (fn (tc,c) => c+(List.length tc)) 0 tcs; *)

(* TODO: 
   simpler to split out InOut events as seperate test cases after generation 

   - need to also apply duplicate elimination as in simconfig
   - counting must be modified to simply use List length
   - setting to distinugush in formatting between unit and system test can be remove *)
						   
fun tc_expandio tc =
  let
      fun isIOEvent (InOutEvent _) = true
	| isIOEvent _ = false;
      
      val (ioevents,tc') = List.partition isIOEvent tc;
      val iotests = List.map (fn ioevent => [ioevent]) ioevents; 
  in
      if (tc' <> [])
      then tc'::iotests
      else iotests
  end

fun tcs_expandio tcs = List.concat (List.map (fn tc => tc_expandio tc) tcs);
  
fun remdupl tcs = List.foldr (fn (tc,tcs) => if (SimConfig.tc_exists tc tcs)
					     then tcs
					     else tc::tcs) [] tcs; 
      
fun sim (n,outr) =
  let
      fun simrun 0 = ()
	| simrun m  =

	  let
	      val tcs = SIMTCG.gen()
	      val _ = (if ((Int.mod(m,outr) = 0))
		       then (let
				val _ = Logging.log ("Simulation   : "^(Int.toString (n-m+1))^":"^(Int.toString n));
				val _ = Logging.log ("Configuration: "^(Config.getConfigName ()));
				val _ = Logging.log ("Steps        : "^(IntInf.toString (step())));
				val _ = Logging.log ("Test cases   : "^(Int.toString (List.length tcs)));
			    in
				()
			    end)
		       else ())

	  in
	      simrun (m-1)
	  end



      val _ = Logging.start ();
      val _ = Logging.sep();
      val _ = Logging.log ("Simulation-based test-case generation");
      val _ = Logging.log ("Configuration: "^(Config.getConfigName ()));
      
      val _ = SimConfig.init();
      val _ = Logging.log ("Test cases start : "^(Int.toString (List.length (SimConfig.getTestcases()))));
      
      val timer = Timer.totalCPUTimer ();

      val t0 = Timer.checkCPUTimer timer;

      val _ = simrun n;

      val t1 = Timer.checkCPUTimer timer;
      val gentime = Time.-(Time.+(#usr t1,#sys t1),Time.+(#usr t0,#sys t0));
      
      val _ = Logging.log ("Completed");
      
      val tcs = remdupl (tcs_expandio (SimConfig.getTestcases()));
      val tcsc = List.length tcs (* tcscount tcs;*) 
      
      val _ = Logging.log ("Total cases  : "^(Int.toString (tcsc)));
      val _ = Logging.sep();
      val _ = Logging.log ("SIM RESULT: "^
			   (Int.toString tcsc)^" "^
			   (Config.getConfigName ())^" "^
			   (Time.toString gentime));
      
      val _ = Logging.sep();
      
      val _ = Logging.stop ();
  in
      tcs 
  end;

(* state-space based test case generation *)

fun ss () =
  let
      val _ = CPN'Sim.init_all(); (* exception raised here earlier ? *)
      val _ = DeleteStateSpace(); 
      val _ = Logging.start ();

      val _ = Logging.sep();
      
      val _ = Logging.log ("State space-based test-case generation");
      val _ = Logging.log ("Configuration: "^(Config.getConfigName ()));

      val _ = Logging.log ("Generating state space ... "^(Int.toString (NoOfNodes ())));

      val timer = Timer.totalCPUTimer ();
      val t0 = Timer.checkCPUTimer timer;
      val _ = CalculateOccGraph();

      val _ = Logging.log ("Completed: "^(Int.toString (NoOfNodes()))^" "^(Int.toString (NoOfArcs())));
      val _ = Logging.log ("Generating test cases ...");

      val tcs = remdupl (tcs_expandio (SSTCG.gen()));

      val t1 = Timer.checkCPUTimer timer;
      val gentime = Time.-(Time.+(#usr t1,#sys t1),Time.+(#usr t0,#sys t0));

      val _ = Logging.log ("Completed");
      val tcsc = List.length tcs (* tcscount tcs; *) 
      
      val _ = Logging.log ("Total cases  : "^(Int.toString (tcsc)));

      val _ = Logging.sep();
      val _ = Logging.log ("SS RESULT: "^
			   (Int.toString tcsc)^" "^
			   (Config.getConfigName ())^" "^
      			   (Time.toString gentime));
      val _ = Logging.sep();
      val _ = Logging.stop ();
  in
      tcs
  end;

fun export (tcs : (TCEvent list) list) = Export.export tcs;

end;
