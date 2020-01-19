structure Export =
struct

(* should eventuelly be added into the Export module of the library *)
fun idnt n = String.concat (List.tabulate(n,fn _ => " "));

fun tag l tagname str = (idnt l)^"<"^tagname^">"^str^"</"^tagname^">\n";
fun tagnl l tagname str = (idnt l)^"<"^tagname^">\n"^str^(idnt l)^"</"^tagname^">\n";

(*
fun testfn testname teststr =
  "<Test TestName=\""^testname^"\">\n"^
  "  <Configuration>\n"^
  Config.formatConfig()^
  "  </Configuration>\n"^
  teststr^
  "</Test>\n";
*)
(*
fun testcasefn (i,teststr) =
  if (not (Config.getTestcaseevent()))
	 then "  <TestCase "^(Config.getTCName i)^">\n"^
	      teststr^
	      "  </TestCase>\n"
  else teststr;
*)

fun setsep _ = ();

fun tc_formatter testcase =
  let
      val inoutevents = List.filter (fn InOutEvent _ => true | _ => false) testcase;
      val testvalues = List.filter (fn InEvent _ => true | _ => false) testcase;
      val testoracles = List.filter (fn OutEvent _ => true | _ => false) testcase;

      (* TODO: numering of unit test cases across several test cases need to be carried forward *)
      (* global numbering of test cases *)

      (* 
      val (_,unitteststr) = (List.foldr
				     (fn (ioevent,(i,str)) =>
						  (i+1,
						   str^"  <TestCase "^(Config.getTCName i)^">\n"^
						   (Config.formatTC ioevent)^
						   "  </TestCase>\n"))	  
				     (1,"")
				     inoutevents)*)
      val (unitteststr,testvaluesstr,testoraclesstr) = Config.TCformat (inoutevents,testvalues,testoracles);
	  (*
      val unitteststr = String.concat (List.map Config.formatTC inoutevents)
      val testvaluesstr = String.concat (List.map Config.formatTC testvalues)
      val testoraclesstr = String.concat (List.map Config.formatTC testoracles)*)
	  
  in
      unitteststr^testvaluesstr^testoraclesstr
  end

(* TODO: eventually move into the configuration module *)
val seperate = ref false;
fun setsep sep = (seperate := sep);
fun sep() = (!seperate);
		
fun output (filename,testname) testfn (testcasefn,tc_formatter) testcases  =
  let
      val file = TextIO.openOut((Config.getOutputDir ())^filename^(!Config.fileext));
      val _ = TextIO.output(file,"<Test TestName=\""^testname^"\">\n"^
				 "  <Configuration>\n"^
				 (Config.formatConfig())^
			         "</Configuration>\n");

      val _ =
	  List.foldr (fn (test,i) =>
			 let
			     val test = Config.normalTC test;
			     val testcasestr = testcasefn (i,tc_formatter test)
			     val _ = TextIO.output(file,testcasestr);
			 in
			     (i+1)
			 end)
		     1
		     testcases;
		    
      val _ = TextIO.output(file,"</Test>\n")
      
      val _ = TextIO.closeOut(file)
  in
      ()
  end

fun output_seperate (filename,testname) testfn (testcasefn,tc_formatter) testcases  =
  let
      val _ = List.foldr (fn (test,i) =>
			     let
				 val testcasestr = testcasefn (i,tc_formatter test)
				 val file = TextIO.openOut((Config.getOutputDir ())^
							   filename^"-"^
							   (Int.toString i)^
							   (!Config.fileext));
				 val teststr = testfn testcasestr		      
				 val _ = TextIO.output(file,teststr)
				 val _ = TextIO.closeOut(file)				 
			     in
				 i+1
			     end)
			 1
			 testcases;
  in
      ()
  end

fun export testcases =
  if (sep()) then output_seperate (Config.getConfigName (),Config.getConfigName ())
				  (Config.TestFn (Config.getConfigName ()))
				  (Config.TCfn,tc_formatter) testcases
  else output (Config.getConfigName (),Config.getConfigName ())
	      (Config.TestFn (Config.getConfigName ()))
	      (Config.TCfn,tc_formatter) testcases;

end;
