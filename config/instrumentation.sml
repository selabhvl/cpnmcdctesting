(* boolean conditions *)

datatype condition = AND of condition * condition
		   | OR of condition * condition
			 | ANDlr of condition * condition
			 | ORlr of condition * condition
		   | NOT of condition
			 | ITE of condition * condition * condition
			 | ITElr of condition * condition * condition
		   | AP of string * bool;

(* TODO: can be implementented more efficient
   - using accumulation and
   - tail recursion

*)

fun countQs (AP(_,_)) = [("?",NONE)]
  | countQs (AND(l,r)) = countQs l^^countQs r
	| countQs (ANDlr(l,r)) = countQs l^^countQs r
	| countQs (OR(l,r)) = countQs l^^countQs r
	| countQs (ORlr(l,r)) = countQs l^^countQs r
	| countQs (NOT(x)) = countQs x
	| countQs (ITE(c,l,r)) = countQs c ^^ countQs l ^^ countQs r
  | countQs (ITElr(c,l,r)) = countQs c ^^ countQs l ^^ countQs r
	;

fun eval (AP (cond,v)) = ([(cond, SOME v)],v)
  | eval (OR (a,b)) =
    let
	val (ares,a') = eval a;
	val (bres,b') = eval b;
    in
	(ares^^bres,a' orelse b')
    end
	| eval (ORlr (a,b)) =
	    let
		val (ares,a') = eval a;
	    in
			if a' then (ares^^countQs b, a' (* true *) )
			      else let val (bres,b') = eval b; in
		             (ares^^bres,(* a' orelse *) b') end
	    end
  | eval (AND (a,b)) =
    let
	val (ares,a') = eval a;
	val (bres,b') = eval b;
    in
	(ares^^bres,a' andalso b')
    end
	| eval (ANDlr (a,b)) =
	    let
		val (ares,a') = eval a
	    in if a' then let val (bres,b') = eval b; in
		                (ares^^bres,(* a' andalso *) b') end
		           else (ares^^countQs b, a' (* false *))
	    end
  | eval (NOT a) =
    let
	val (ares,a') = eval a;
    in
	(ares,not a')
	  end
 | eval (ITE (c,l,r)) =
 	 let
			val (cres,c') = eval c;
			val (lres,l') = eval l;
			val (rres,r') = eval r;
	 in (cres^^lres^^rres, (c' andalso l') orelse r')
	 end
	| eval (ITElr (c,l,r)) =
  	let
	 		val (cres,c') = eval c;
		in if c' then let
	 		    val (lres,l') = eval l;
			    in (cres^^lres^^countQs r, l') end
			 else let
	 		    val (rres,r') = eval r;
	 	      in (cres^^countQs l^^rres, r') end
    end;


fun resToString res =
  String.concat (
  List.map
      (fn (cond,v) => (case v of NONE => "?"
				| SOME b => if b then "1" else "0"))
      res);

fun EXPR (name,expr) =
  let
      val (res,expr') = eval expr;
      val _ = Logging.log (name^":"^resToString res^":"^(if expr' then "1" else "0"));
  in
      expr'
  end
