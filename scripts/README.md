# Running Scripts

## Prerequisites
Before running the scripts, ensure you have created the conda environment as described in the main README.

## Running the Scripts
Once the conda environment is set up, you can run the scripts using the `go.run_scripts.sh` script.
You also have to enter the run_jidt directory and follow the instructions in the README.md file to run the Java JIDT scripts.
Once run both the Python and Java scripts, you can generate the figures on the notebooks.

## Running the python libraries scripts
To run the `go.run_scripts.sh` script, use the following command after activating the conda environment:
```sh
./go.run_scripts.sh
```

## Explanation of `go.run_scripts.sh`
The `go.run_scripts.sh` script is a shell script that automates the execution of various Python scripts in this directory. It ensures that the necessary parameters are set as run for the results of the paper. For a more detailed view, check the `go.run_scripts.sh` script to understand the specific scripts it runs at it's also suppose to be a declarative file to have a broad view of all the run scripts.

## Running the Java JIDT scripts
To run the Java JIDT scripts, you can enter the run_jidt directory and follow the instructions in the README.md file.