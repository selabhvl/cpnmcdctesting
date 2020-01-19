fun b() = (use (mbtcpnlibpath^"build.sml"));

fun ss() = (use (modelpath^"tcg.sml");
	    use (modelpath^"tcg-common.sml"));

fun si() = (use (modelpath^"tcg-common.sml"));

fun boot() = (use (mbtcpnlibpath^"config/simconfig.sml");
	      use (mbtcpnlibpath^"config/config.sml");
	      use (modelpath^"tcg-common.sml"));

use (mbtcpnlibpath^"config/config.sml"); (* REMOVE ? *)

use (mbtcpnlibpath^"config/logging.sml");

use (mbtcpnlibpath^"compute/tcspec-sig.sml");

use (mbtcpnlibpath^"compute/sstcg.sml");
use (mbtcpnlibpath^"compute/simtcg.sml");


use (mbtcpnlibpath^"export/export.sml");

use (mbtcpnlibpath^"compute/tcg-sig.sml");

use (mbtcpnlibpath^"execute/execute.sml");

use (mbtcpnlibpath^"execute/run.sml");

		   

