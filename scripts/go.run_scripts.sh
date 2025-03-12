#######################################
#### Run computation time analysis ####
#######################################


python run_time_by_order_HOI_toolbox.py \
    --min_T 1000 \
    --min_N 30 \
    --min_order 3 --max_order 31 \
    --output_path ../results/times/time_by_order_library-hoitoolbox.tsv

python run_time_by_order_HOI.py \
    --min_T 1000 \
    --min_N 30 \
    --min_order 3 --max_order 31 \
    --output_path ../results/times/time_by_order_library-hoi.tsv

python run_time_by_order_THOI.py \
    --min_T 1000 \
    --min_N 30 \
    --min_bs 10000 \
    --min_order 3 --max_order 31 \
    --indexing_method indexes --use_cpu \
    --output_path ../results/times/time_by_order_library-thoi.tsv


########################################################
#### Run computation time per sample size analysis #####
########################################################


python run_time_by_sample_size_HOI_toolbox.py \
    --files_dir ../data/random_sample_sizes \
    --output_path ../results/times/time_by_sample_size_library-hoitoolbox.tsv

python run_time_by_sample_size_HOI.py \
    --files_dir ../data/random_sample_sizes \
    --output_path ../results/times/time_by_sample_size_library-hoi.tsv

python run_time_by_sample_size_THOI.py \
    --files_dir ../ /random_sample_sizes \
    --output_path ../results/times/time_by_sample_size_library-thoi.tsv


#######################################
######### RUN ANESTHESIA ##############
#######################################


python run_anesthesia.py \
    --input_path ../data/fmri_anesthesia/42003_2023_5063_MOESM3_ESM/nets_by_subject \
    --output_path ../results/anesthesia/
