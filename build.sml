fun b() = (use (mbtcpnlibpath^"build.sml"));

fun ss() = (use (modelpath^"tcg.sml");
	    use (modelpath^"tcg-common.sml"));

fun si() = (use (modelpath^"tcg-common.sml"));

fun boot() = (use (mbtcpnlibpath^"config/simconfig.sml");
	      use (mbtcpnlibpath^"config/config.sml");
	      use (modelpath^"tcg-common.sml"));

use (mbtcpnlibpath^"execute/execute.sml");

use (mbtcpnlibpath^"execute/run.sml");

		   

