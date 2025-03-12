# Compile and run

## RunMeasureTimesJDIT
javac -cp infodynamics.jar RandomSystemsGenerator.java TSVWriter.java RunMeasureTimesJDIT.java
java -cp .:infodynamics.jar RunMeasureTimesJDIT ../../results/times/time_by_order_library-jdit.tsv

## RunOinfoTimeBySampleSize
javac -cp infodynamics.jar TSVWriter.java CSVReader.java RunOinfoTimeBySampleSize.java
java -cp .:infodynamics.jar RunOinfoTimeBySampleSize ../../data/random_sample_sizes ../../results/times/time_by_sample_size_library-jidt.tsv
