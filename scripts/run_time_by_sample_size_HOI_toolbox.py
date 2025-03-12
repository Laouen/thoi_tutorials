import pandas as pd
import os
import sys
import time
from glob import glob
from tqdm import tqdm
from argparse import ArgumentParser
import numpy as np

HOI_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'HOI_toolbox')  # This gets the directory where main.py is located
sys.path.append(HOI_dir)
print('HOI Toolbox dir added to path:', HOI_dir)

from toolbox.Oinfo import exhaustive_loop_zerolag

# Create an alias to handle deprecated np.float usage as its deprecated in new numpy versions
if not hasattr(np, 'float'):
    np.float = float  # Redirect np.float to built-in float type

def main(files_dir: str, output_path: str):
    """
    Measure the runtime of HOI toolbox for different sample sizes.

    Parameters:
    - files_dir (str): Directory containing the input CSV files with sample data.
    - output_path (str): Path to the output CSV file to store the results.

    Returns:
    None
    """
    # get all files
    files = glob(os.path.join(files_dir, f"nsamples-*_nvars-10.csv"))

    config = {
        "higher_order": False,
        "estimator": 'gcmi',
        "n_best": 10, 
        "nboot": 10,
        'minsize': 10,
        'maxsize': 10
    }

    rows = []
    pbar = tqdm(files)
    for file in pbar:
        X = pd.read_csv(file, header=None).values
        X = X.T
        N, T = X.shape
        pbar.set_description(f"T={T}:")

        for i in range(100):

            start = time.time()
            exhaustive_loop_zerolag(X, config)
            delta_t = time.time() - start

            rows.append([T, i, delta_t])
    
    pd.DataFrame(rows, columns=['sample size', 'iteration', 'time']).to_csv(output_path, sep='\t', index=False)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--files_dir", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    args = parser.parse_args()

    main(args.files_dir, args.output_path)