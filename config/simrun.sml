fun mcdcgen (logfilename) =
  let
      val _ = Logging.start(logfilename);

      val _ = Logging.log "MCDC instrumentation started";

      val _ = CPN'Sim.init_all();
      val _ = CPN'Sim.run();

      val _ = Logging.log "MCDC instrumentation stopped";
      val _ = Logging.stop();

  in
      ()
  end;
