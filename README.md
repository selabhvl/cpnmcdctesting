# Coverage Analysis of Net Inscriptions in Coloured Petri Net Models

This repository contains our library for measuring MC/DC and branch coverage
on Coloured Petri net models (CPN) from within [CPNTools](http://cpntools.org).

Our library is based on instrumenting conditional expressions in the SML
expressions on arcs and guards, and a Python script that collects and processes
the recorded data. It can be used both with state space exploration and
simulation.

The original models are from:
* CPNABS: https://github.com/natasa-gkolfi/cpnabs
* Paxos:
* MQTT:
* [TODO: @fahishakiye]

You can read more about our testing library in our forthcoming publication.

This work is supported through the [EU H2020 project COEMS](https://www.coems.eu).

## USAGE
- open your model in CPNTools
- open the State Space tool and
  run state space exploration (with `timeout=1`), so that the required SML
  functions become available
- include the library into your model through `use` (see e.g. example models),  
right-click and evaluate the `use`-expression
- annotate boolean decisions with `EXPR`-invocations in your model
- invoke one of the `mcdcgen`-functions (with/without timeout, with one or more
  configurations)

When you have recorded enough data, process the logfile through the Python
script. This will generate... [TODO: @nrequeno]

## TODO

- we should have timestamps in the logfile (@VolkerStolz)
- how to use together with simulation (@lmkr)
