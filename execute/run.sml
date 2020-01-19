(* model-dependent configuration of test case generation *)
datatype strategy = SS | SIM of int;

fun run SS _ =
  let
      val name = Config.getConfigName();
      val _ = Config.setConfigNaming (fn () => "ss-"^name);
      val tcs = Execute.ss()
      val _ = Execute.export tcs
  in
      Config.setConfigNaming (fn () => name)
  end
  | run (SIM m) outr =
    let
	val name = Config.getConfigName();
	val _ = Config.setConfigNaming (fn () => "si-"^(Int.toString m)^"-"^name);

        val tcs = Execute.sim (m,outr)
        val _ = Execute.export tcs
    in
      Config.setConfigNaming (fn () => name)
    end

fun runall outr configs = List.app (fn config => run config outr) configs;

(*
fun run config =
  let
      val _ = Config.setModelDir mbtcpnlibpath;
      val _ = Logging.start();
      val _ = Execute.ss();
      val _ = Logging.stop ();
  in
      ()
  end;
*)
