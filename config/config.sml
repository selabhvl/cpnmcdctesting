structure Config =
struct

  val modeldir = ref "";
  fun getModelDir () = (!modeldir);
  fun setModelDir outdir = (modeldir := outdir);
  
  (* output directory where files are stored *)
  val tcoutputdir = ref "testcases/";
  fun getOutputDir () = (!tcoutputdir);
  fun setOutputDir outdir = (tcoutputdir := outdir);

  (* for naming file holding a set of test cases *)
  val confignaming = ref (fn () => "tcs");
  fun setConfigNaming namingfn = (confignaming := namingfn);
  fun getConfigName () = (!confignaming ());

    (* test cases per event *)
  val testcaseevent = ref false; (* true for single event test case generation *)
  fun setTestcaseevent bf = (testcaseevent := bf);
  fun getTestcaseevent () = (!testcaseevent);

  val fileext = ref ".xml";
  
  (* for naming individual test cases *)
  val tcnaming = ref (fn i => Int.toString i);
  fun setTCNaming namingfn = (tcnaming := namingfn);
  fun getTCName i = (!tcnaming i);

  (* event detection function *)
  val tcdetect = ref (fn (x:Bind.Elem) => false);
  fun setTCdetect detectfn = (tcdetect := detectfn);
  fun detectTC event = (!tcdetect event);

  (* observation function *)
  val tcobserve = ref (fn (x:Bind.Elem) => [] : TCEvent list);
  fun setTCobserve observefn = (tcobserve := observefn);
  fun observeTC event = (!tcobserve event);

  (* formatting  function *)
  val tceventformat = ref (fn (x:TCEvent) => "");
  fun setTCeventformat formatfn = (tceventformat := formatfn);
  fun formatTCevent event = (!tceventformat event);

  val tcformat = ref (fn (inoutevents, testvalues, testoracles) =>
			 let
			     val unitteststr = String.concat (List.map formatTCevent inoutevents)
			     val testvaluesstr = String.concat (List.map formatTCevent testvalues)
			     val testoraclesstr = String.concat (List.map formatTCevent testoracles)
			 in
			     (unitteststr,
			     (if testvaluesstr <> ""
			      then "    <TestValues>\n"^testvaluesstr^"    </TestValues>\n"
			      else ""),
			     (if testoraclesstr <> ""
			      then "    <TestOracles>\n"^testoraclesstr^"    </TestOracles>\n"
			      else ""))
			 end);
  
  fun setTCformat newtcformat = (tcformat := newtcformat);
  fun TCformat (inoutevents, testvalues, testoracles) = (!tcformat (inoutevents, testvalues, testoracles));
					 
  (* formatting embedding each test case *)
  val tcfn = ref (fn (i,teststr) =>
		     if (not (getTestcaseevent()))
		     then "  <TestCase "^(getTCName i)^">\n"^
			  teststr^
			  "  </TestCase>\n"
		     else teststr);

  fun setTCfn testcasefn = (tcfn := testcasefn);
  fun TCfn (i,teststr) = (!tcfn (i,teststr));

    (* configuration information for the test *)
  val configformat = ref (fn () => "");
  fun setConfigformat configformatfn = (configformat := configformatfn);
  fun formatConfig () = (!configformat ());

  (* formatting embeddeding each test *)
  val testfn = ref (fn (testname,teststr) =>
		       "<Test TestName=\""^testname^"\">\n"^
		       "  <Configuration>\n"^
		       formatConfig()^
		       "  </Configuration>\n"^
		       teststr^
		       "</Test>\n");

  fun setTestfn newtestfn = (testfn := newtestfn);
  fun TestFn testname teststr = (!testfn (testname,teststr));


  (* normalisation function for test case events *)
  val tcnormal = ref (fn (tce : (TCEvent list)) => (tce: TCEvent list));
  fun setTCnormal confignormalfn = (tcnormal := confignormalfn);
  fun normalTC tce = (!tcnormal tce);
  
  (* TODO: oracle detection and observation *)
  (* may need to go into a seperate monitor *)

  
end;
