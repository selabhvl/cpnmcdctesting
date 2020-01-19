structure SimConfig = 
struct

(* add x to xs if not already present *)
fun add (x,xs) = if (List.exists (fn x' => x = x') xs) then xs else x::xs 

fun merge dl sl = List.foldr (fn (x,dl) => add (x,dl)) dl sl;

									   
val testcases = ref ([] : (TCEvent list) list);

val testcase = ref ([] : (TCEvent list));

fun clear () = (testcase := []);

fun getTestcases () = (!testcases);

fun observe tcevents = (testcase := (merge tcevents (!testcase));0); 
  
fun init() = (testcases := [];
	      testcase := []);

fun tc_contain tc1 tc2 =
  List.all (fn ev => List.exists (fn ev' => ev = ev') tc2) tc1;

fun tc_equal tc1 tc2 = (tc_contain tc1 tc2) andalso (tc_contain tc2 tc1);

fun tc_exists tc tcs = List.exists (fn tc' => tc_equal tc tc') tcs;

fun stop() =
  let
      val _ = if tc_exists (!testcase) (!testcases)
	      then ()
	      else (testcases := (!testcase)::(!testcases));
  in
      testcase := []
  end;

end

(* dummy structures for sim-based test case generation *)
structure Bind =
struct
type Elem = int;
end;

fun OutArcs _ = [];
fun OutNodes _ = [];
fun DestNode _ = 1;
fun NoOfNodes () = 1;
val InitNode = 1;
fun ListDeadMarkings () = [];
fun ArcToBE _ = 1;
fun DeleteStateSpace () = ();
fun CalculateOccGraph () = ();
fun NoOfArcs () = 1;
