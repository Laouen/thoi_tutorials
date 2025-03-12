# Compile and run

## Prerequisites
Make sure you have Java installed and working on your system. You can check your Java installation by running:
```sh
java -version
```
If Java is not installed, you can download and install it from [here](https://www.java.com/en/download/).

## RunMeasureTimesJDIT
```sh
javac -cp infodynamics.jar RandomSystemsGenerator.java TSVWriter.java RunMeasureTimesJDIT.java
java -cp .:infodynamics.jar RunMeasureTimesJDIT ../../results/times/time_by_order_library-jdit.tsv
```

## RunOinfoTimeBySampleSize
```sh
javac -cp infodynamics.jar TSVWriter.java CSVReader.java RunOinfoTimeBySampleSize.java
java -cp .:infodynamics.jar RunOinfoTimeBySampleSize ../../data/random_sample_sizes ../../results/times/time_by_sample_size_library-jidt.tsv
```
