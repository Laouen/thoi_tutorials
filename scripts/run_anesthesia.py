from glob import glob
import os
from argparse import ArgumentParser
from pathlib import Path

import pandas as pd
import numpy as np

from scipy.stats import wilcoxon

from thoi.heuristics.simulated_annealing_multi_order import simulated_annealing_multi_order
from thoi.heuristics import greedy

import torch

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score
import pingouin as pg


import time

def effect_size(batched_res: torch.Tensor, metric:str='o'):
    '''
    Get the effect size of the groups from the batched results.

    params:
    - batched_res (np.ndarray): The batched results with shape (batch_size, D, 4) where 4 is the number of metrics (tc, dtc, o, s). D = 2*n_subjects where [0, D/2) are from the group 1 and [D/2, D) are from the group 2.
    - metric (str): The metric to test the difference. One of tc, dtc, o or s
    '''
    
    METRICS = ['tc', 'dtc', 'o', 's']
    metric_idx = METRICS.index(metric)
    
    batch_size, D = batched_res.shape[:2]
    
    # |batch_size| x |D/2|
    group1 = batched_res[:, :D//2, metric_idx]
    group2 = batched_res[:, D//2:, metric_idx]
    
    # for each batch item compute the wilcoxon test
    # |batch_size|
    # groups are ordererd as group2, group1 to get positive effect size when group2 is greater than group1
    effect_size = torch.tensor([
        pg.compute_effsize(group2[i].cpu().numpy(), group1[i].cpu().numpy(), paired=True, eftype='cohen')
        for i in range(batch_size)
    ])
    
    # make absolute the effect size
    return effect_size

def auc_metric(batched_res: torch.Tensor, metric:str='o'):
    
    '''
    Get the roc auc score of the droups differences from the batched results.

    params:
    - batched_res (np.ndarray): The batched results with shape (batch_size, D, 4) where 4 is the number of metrics (tc, dtc, o, s). D = 2*n_subjects where [0, D/2) are from the group 1 and [D/2, D) are from the group 2.
    - metric (str): The metric to test the difference. One of tc, dtc, o or s
    '''
    
    METRICS = ['tc', 'dtc', 'o', 's']
    metric_idx = METRICS.index(metric)

    n_subjects = batched_res.shape[1] // 2    
    
    # Prepare de data    
    batched_X = batched_res[..., metric_idx].cpu().numpy()
    y = np.concatenate([np.zeros(n_subjects), np.ones(n_subjects)])
    
    # Prepare the output
    total_auc = torch.tensor([roc_auc_score(y, X) for X in batched_X])
    
    # get absolute distance from 0.5
    return total_auc - 0.5

def read(data_dir: str):
    
    states_all = ['Awake', 'Deep']

    dfs_dict = {}
    for state in states_all:
        # list all folder in data_dir/state
        folders = glob(os.path.join(data_dir, state, '*'))
        for folder in folders:
            network = os.path.basename(folder).replace('_parcellation_5', '')
            
            # List all csv files in folder
            csv_files = glob(os.path.join(folder, f'ts_{network}_parcellation_5_Sub*.csv'))
            for csv_file in csv_files:
                sub = int(os.path.basename(csv_file).split('_')[-1].split('.')[0].replace('Sub', ''))
                
                # Read csv file and add information columns
                df = pd.read_csv(csv_file, sep=',', header=None)
                
                # Convert the columns in multilavel, add the network to a second lavel
                df.columns = pd.MultiIndex.from_product([[network], range(df.shape[1])])
                
                # Add df to dfs dict
                if sub not in dfs_dict:
                    dfs_dict[sub] = {}
                
                if state not in dfs_dict[sub]:
                    dfs_dict[sub][state] = []
                
                dfs_dict[sub][state].append(df)

    # Concatenate all dataframes into a single one
    dfs_list = []
    for sub, states in dfs_dict.items():
        for state, dfs in states.items():
            df = pd.concat(dfs, axis=1)
            df['sub'] = sub
            df['state'] = state
            df = df[[('sub',''), ('state','')] + [col for col in df.columns if col[0] not in ['sub', 'state']]]
            dfs_list.append(df)

    df = pd.concat(dfs_list, axis=0)

    # Remove sub10 that has no some missing networks
    df = df[df['sub'] != 10]

    # Check Show missing values (should be none), all subjects have all the networks
    assert df.isnull().sum().sum() == 0, 'There are missing values'

    # Check all subjects have same lenght across states and networks
    assert df.groupby(['sub','state']).size().unique() == [245], 'Series lenght is not the same for all subjects'

    networks = df.columns.get_level_values(0).unique()[2:]
    #network_pairs = list(combinations(networks, 2))

    # Create the list of datsa
    Xs = [
        df[(df['sub'] == sub) & (df['state'] == state)][networks].values
        for state in states_all
        for sub in sorted(df['sub'].unique())
    ]

    return df, Xs

def run_greedy(Xs, root, largest):
    
    print('Running greedy')
    nplets, scores = greedy(Xs, repeat=50, metric=effect_size, largest=largest)
    
    # save the results as npy files
    np.save(os.path.join(root, f'nplets_greedy_effect_size_{"max" if largest else "min"}.npy'), nplets.numpy())
    np.save(os.path.join(root, f'scores_greedy_effect_size_{"max" if largest else "min"}.npy'), scores.numpy())

def run_annealing(Xs, root, largest):

    print('Running annealing')
    nplets, scores = simulated_annealing_multi_order(Xs, repeat=50, metric=effect_size, largest=largest)

    # save the results as npy files
    np.save(os.path.join(root, f'nplets_annealing_effect_size_{"max" if largest else "min"}.npy'), nplets.numpy())
    np.save(os.path.join(root, f'scores_annealing_effect_size_{"max" if largest else "min"}.npy'), scores.numpy())
    
def run_wale(Xs, root):
    Xs_awake = Xs[:16]
    Xs_deep = Xs[16:]
    
    nplets_awake_max, scores_awake_max = greedy(Xs_awake, repeat=50, metric='o', largest=True)
    nplets_awake_min, scores_awake_min = greedy(Xs_awake, repeat=50, metric='o', largest=False)

    nplets_deep_max, scores_deep_max = greedy(Xs_deep, repeat=50, metric='o', largest=True)
    nplets_deep_min, scores_deep_min = greedy(Xs_deep, repeat=50, metric='o', largest=False)
    

    # save the results as npy files
    np.save(os.path.join(root, 'nplets_greedy_awake_max.npy'), nplets_awake_max.numpy())
    np.save(os.path.join(root, 'nplets_greedy_awake_min.npy'), nplets_awake_min.numpy())
    
    np.save(os.path.join(root, 'scores_greedy_awake_max.npy'), scores_awake_max.numpy())
    np.save(os.path.join(root, 'scores_greedy_awake_min.npy'), scores_awake_min.numpy())
    
    np.save(os.path.join(root, 'nplets_greedy_deep_max.npy'), nplets_deep_max.numpy())
    np.save(os.path.join(root, 'nplets_greedy_deep_min.npy'), nplets_deep_min.numpy())
    
    np.save(os.path.join(root, 'scores_greedy_deep_max.npy'), scores_deep_max.numpy())
    np.save(os.path.join(root, 'scores_greedy_deep_min.npy'), scores_deep_min.numpy())
    
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--output_path', type=str)
    parser.add_argument('--input_path', type=str)
    
    args = parser.parse_args()
    
    df, Xs = read(args.input_path)
    
    Path(args.output_path).mkdir(parents=True, exist_ok=True)
    
    run_greedy(Xs, args.output_path, True)
    run_greedy(Xs, args.output_path, False)
    run_annealing(Xs, args.output_path, True)
    run_annealing(Xs, args.output_path, False)
    run_wale(Xs, args.output_path)
    
    print('FINISHED')