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
* [TODO: @fahishakiye]

You can read more about our testing library in our forthcoming publication.

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
script. This will generate... [TODO: @nrequeno]

## TODO

- we should have timestamps in the logfile (@VolkerStolz)
- how to use together with simulation (@lmkr)
