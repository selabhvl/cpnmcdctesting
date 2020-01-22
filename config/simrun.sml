fun mcdcgen () =
  let
      val _ = Logging.start();
      
      val _ = Logging.log "MCDC instrumentation started";
      
      val _ = CPN'Sim.init_all();
      val _ = CPN'Sim.run();

      val _ = Logging.log "MCDC instrumentation stopped";
      val _ = Logging.stop();

  in
      ()
  end;
