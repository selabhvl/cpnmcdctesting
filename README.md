# Coverage Analysis of Net Inscriptions in Coloured Petri Net Models

This repository contains our library for measuring MC/DC and branch coverage
on Coloured Petri net models (CPN) from within [CPNTools](http://cpntools.org).

Our library is based on instrumenting conditional expressions in the SML
expressions on arcs and guards, and a Python script that collects and processes
the recorded data. It can be used both with state space exploration and
simulation.

The original models are from:
* CPNABS: https://github.com/natasa-gkolfi/cpnabs
* Paxos: https://github.com/selabhvl/singleDecreePaxosCPN
* DisCSP: https://github.com/carlospascal/DisCSP-CPN-Models
* MQTT: https://bitbucket.org/alejandrort/mqtt-cpn-public/

You can read more about our testing library in our forthcoming publication,
please see [the arXiv preprint](https://arxiv.org/abs/2005.09806).

This work is supported through the [EU H2020 project COEMS](https://www.coems.eu).

## USAGE
- Open your model in CPNTools (download available at http://cpntools.org/)
- Open the State Space tool and
  run state space exploration (with `timeout=1`), so that the required SML
  functions become available
- Set the path to instrumentation library (e.g `val cpnmcdclibpath =  "path/to/library";`)
- Include the library into your model through `use` (see e.g. example models),
  * `use (cpnmcdclibpath^"config/logging.sml");`
  * `use (cpnmcdclibpath^"config/instrumentation.sml");`
  * `use (cpnmcdclibpath^"boot.sml");`
  * `use (cpnmcdclibpath^"config/simrun.sml");`

-  To evaluate the `use`-expression, right-click and evaluate
- Annotate Boolean decisions with `EXPR`-invocations in your model for example:
 * The decision : `a > 0 andalso (b orelse (c = 42))`
 * Can be transformed into: `EXPR("decision_name", AND(AP("1", a>0), OR(AP("2",b), AP("3", c=42))))`
- MC/DC tool invocation:
  * right-click and evaluate the `use (cpnmcdclibpath^"config/simrun.sml");`
  * invoke one of the `mcdcgen`-functions (with/without timeout, with one or more
  configurations) `mcdcgen("path/to/filename.log");`


When you have recorded enough data, process the logfile through the Python
scripts in the python/doc folder. The command: 

```
$ python doc/demo.py execution_trace.log
```

 parses the `execution_trace.log` file and calculates coverage information. It prints individual reports in the form of the truth tables for each decision, which summarises the conditions that are fired during the execution of the CPN model.
   
In the case that the decision is not MC/DC covered, the Python script points out the remaining valuations of the truth tables that should be evaluated in order to fulfil this criteria. 

Additionally, 

```
$ python doc/report.py execution_trace.log gnu_plot.data (num_PN_transitions)
```

will process the `execution_trace.log` file and report the percentage of transitions in the Petri net that satisfy the MC/DC and branch coverage criteria. 
 The output file is in the GNU Plot format, so that it can be later easily plotted by running the following command:
 
 ```
 plot "gnu_plot.data" using 1:2 title 'MCDC' with lines,\
     "gnu_plot.data" using 1:3 title 'BC' with lines
```
More details about the installation and usage of the Python script are found in the python/README.md file.

## TODO

- we should have timestamps in the logfile (@VolkerStolz)
- how to use together with simulation (@lmkr)
