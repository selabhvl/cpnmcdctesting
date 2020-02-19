fun mcdcgen (logfilename) =
  let
      val _ = Logging.start(logfilename);

      val _ = Logging.log "MCDC instrumentation started";

      val _ = CPN'Sim.init_all();
      (* If this bails out, you did not load the SS-tool in the model yet *)
      val _ = DeleteStateSpace();
      val _ = CalculateOccGraph();

      val _ = Logging.log "MCDC instrumentation stopped";
      val _ = Logging.stop();

  in
      ()
  end;
