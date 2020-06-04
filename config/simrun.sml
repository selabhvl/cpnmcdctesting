
fun profile f =
  let
      val cputimer = Timer.startCPUTimer();

      val _ = f ();

      val {usr,sys} = Timer.checkCPUTimer cputimer;
      val cputime = Time.+(usr,sys);
  in
      "CPU time[" ^ Time.toString cputime ^ "]"
  end;

fun mcdcgenConfig (timeout, applyConfig, cs, logfilename) =
  let
      val _ = Logging.start(logfilename);

      val _ = Logging.log "MCDC instrumentation started";

      val _ = CPN'Sim.init_all();
      val _ = OGSet.StopOptions{
        Nodes = NoLimit,
        Arcs = NoLimit,
        Secs = timeout,
        Predicate = fn _ => false
      };
      (* If this bails out, you did not load the SS-tool in the model yet *)
      (* We always run the base-model first. It's easy to roll your own driver *)
      val _ = DeleteStateSpace();
      val _ = Logging.log "default configuration"
      val profstr = profile CalculateOccGraph;
      val _ = Logging.log profstr;
      
      (* Any further configurations? *)
      val _ = List.foldl (fn (c,cnt) => let
        val _ = DeleteStateSpace();
        val _ = Logging.log ("run " ^ Int.toString cnt)
        val _ = applyConfig c;
        val profstr = profile (CalculateOccGraph);
	val _ = Logging.log profstr;
        in (cnt+1) end
      ) 1 cs;
      val _ = Logging.log "MCDC instrumentation stopped";
      val _ = Logging.stop();
  in
      ()
  end;

fun mcdcgenTimeout (timeout, logfilename) = mcdcgenConfig(timeout,fn f =>f,[],logfilename);
fun mcdcgen (logfilename) = mcdcgenTimeout(0,logfilename);
