structure Logging =
struct

val logfilename = "mbtcpn.log";

val file = ref (NONE :(TextIO.outstream option));

fun log msg =
  case (!file) of
      NONE => ()
   |  SOME (stream) =>
      let
	  val time = Date.toString(Date.fromTimeLocal(Time.now()));
	  val _ = TextIO.output(stream,time^" "^msg^"\n")
      in
	  TextIO.flushOut(stream)
      end;

fun start () =
  let
      val filename = Config.getOutputDir()^logfilename
  in
      (case (!file) of
	   NONE => (file := SOME (TextIO.openAppend(filename));
		    log "Logging started")
	| SOME _ => ()) 
  end; 

fun stop() =
  case (!file) of
      NONE => ()
    | SOME(stream) => (log "Logging stopped";
		       TextIO.closeOut(stream);
		       file := NONE);

fun sep() = log ("===========================================");
  
end;
