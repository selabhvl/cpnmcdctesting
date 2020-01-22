(* boolean conditions *)

datatype condition = AND of condition * condition
		   | OR of condition * condition
		   | NOT of condition
		   | AP of string * bool;

(* TODO: can be implementented more efficient 
   - using accumulation and 
   - tail recursion 

*)

fun eval (AP (cond,v)) = ([(cond,v)],v)
  | eval (OR (a,b)) =
    let
	val (ares,a') = eval a;
	val (bres,b') = eval b;
    in
	(ares^^bres,a' orelse b')
    end
  | eval (AND (a,b)) =
    let
	val (ares,a') = eval a;
	val (bres,b') = eval b;
    in
	(ares^^bres,a' andalso b')
    end
  | eval (NOT a) =
    let
	val (ares,a') = eval a;
    in
	(ares,not a')
    end;

fun resToString res =
  String.concat (
  List.map
      (fn (cond,v) => cond^(Bool.toString v)^" ")
      res);
      
fun EXPR (name,expr) =
  let
      val (res,expr') = eval expr;

      val _ = Logging.log (name^":"^resToString res^"->"^(Bool.toString expr'));
  in
      expr'
  end

