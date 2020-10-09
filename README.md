# Parallelization-of-Rabin-Karp-Algorithm

# Requirements:
Windows 10<br>
Python 3<br>
Pip

# Installation:
1. Download the latest version of MS-MPI from https://www.microsoft.com/en-us/download/details.aspx?id=100593
2. Run both the files
3. Add C:\Program Files (x86)\Microsoft SDKs\MPI to Path user environment variable
4. run "pip install mpi4py" in cmd

# Execution
Open cmd<br>
cd [location of folder]<br>
Serial: python RabinKarpSerial.py filenames.txt multipattern.txt<br>
Parallel: mpiexec -n [no of processors] python pdc_parallel.py filenames.txt multipattern.txt<br>

To check availble no of processors on your system:<br>
Ctrl + Shift + Esc>Performance>Logical Processors
