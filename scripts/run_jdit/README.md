# Compile and run

## RunMeasureTimesJDIT
javac -cp infodynamics.jar RandomSystemsGenerator.java TSVWriter.java RunMeasureTimesJDIT.java
java -cp .:infodynamics.jar RunMeasureTimesJDIT ../results/times/library-jdit_estimator-ksg.tsv

## RunMeasuresInSamples
javac -cp infodynamics.jar TSVWriter.java CSVReader.java RunMeasuresInSamples.java
java -cp .:infodynamics.jar RunMeasuresInSamples /home/laouen.belloli/Documents/data/Oinfo/PGM_data /home/laouen.belloli/Documents/git/Oinformation/benchmarking/results/pgm/pgm_results_jidt.tsv

## RunOinfoTimeBySampleSize
javac -cp infodynamics.jar TSVWriter.java CSVReader.java RunOinfoTimeBySampleSize.java
java -cp .:infodynamics.jar RunOinfoTimeBySampleSize /home/laouen.belloli/Documents/data/Oinfo/random_sample_sizes /home/laouen.belloli/Documents/git/Oinformation/benchmarking/results/times/by_sample_size_library-jidt.tsv
