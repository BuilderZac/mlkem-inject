# mlkem-inject
A injection framework for ML-KEM decap phase
To use this run the ./start.sh script. This will launch gdb & trigger the python script to control it. Once started it will go into a holding pattern waiting for the "demoUse" program to start. Once demoUse is found as an active process it will attach to it & start doing the injection automatically.
