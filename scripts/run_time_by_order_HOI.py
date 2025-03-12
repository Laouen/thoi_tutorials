import pandas as pd
import numpy as np
import time
from tqdm import trange
import argparse
import hoi
from pathlib import Path


def main(min_T, step_T, max_T, min_N, step_N, max_N, min_order, max_order, output_path):
    """
    Measure the runtime of HOI toolbox for different configurations.

    Parameters:
    - min_T (int): Minimum number of samples.
    - step_T (int): Step size for the number of samples.
    - max_T (int): Maximum number of samples.
    - min_N (int): Minimum number of features.
    - step_N (int): Step size for the number of features.
    - max_N (int): Maximum number of features.
    - min_order (int): Minimum size of the n-plets.
    - max_order (int): Maximum size of the n-plets.
    - output_path (str): Path to the output .tsv file to store the results.

    Returns:
    None
    """
    max_T = min_T if max_T is None else max_T
    max_N = min_N if max_N is None else max_N
    max_order = min_order if max_order is None else max_order

    assert min_order <= max_order, f'min_order must be <= max_order. {min_order} > {max_order}'
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for T in trange(min_T, max_T+1, step_T, leave=False, desc='T'): 
        for N in trange(min_N, max_N+1, step_N, leave=False, desc='N'):
            
            X = np.random.rand(T, N)

            for order in trange(min_order, max_order+1, leave=False, desc='Order'):

                if order > N:
                    continue

                try:
                    start = time.time()
                    h = hoi.metrics.Oinfo(X)
                    h.fit(order, order, method='gc')
                    delta_t = time.time() - start
                except MemoryError as me: # Handle MemoryError
                    delta_t = -1
                except Exception as e: # Handle other exceptions
                    delta_t = -1

                rows.append(['HOI', 'GC', T, N, order, delta_t])

                pd.DataFrame(
                    rows,
                    columns=['library', 'estimator', 'T', 'N', 'order', 'time']
                ).to_csv(output_path, sep='\t', index=False)


if __name__ == '__main__':

    parser = argparse.ArgumentParser('Test run time for HOI O information')
    parser.add_argument('--min_T', type=int, help='Min number of samples')
    parser.add_argument('--step_T', type=int, help='Step for number of samples', default=1)
    parser.add_argument('--max_T', type=int, help='Max number of samples', default=None)
    parser.add_argument('--min_N', type=int, help='Min number of features')
    parser.add_argument('--step_N', type=int, help='Step for number of features', default=1)
    parser.add_argument('--max_N', type=int, help='Max number of features', default=None)
    parser.add_argument('--min_order', type=int, help='Min size of the n-plets')
    parser.add_argument('--max_order', type=int, help='Max size of the n-plets', default=None)
    parser.add_argument('--output_path', type=str, help='Path of the .tsv file where to store the results')

    args = parser.parse_args()

    main(args.min_T, args.step_T, args.max_T,
         args.min_N, args.step_N, args.max_N,
         args.min_order, args.max_order,
         args.output_path)