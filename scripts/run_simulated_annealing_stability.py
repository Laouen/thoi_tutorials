import numpy as np
from tqdm import tqdm
from thoi.heuristics import simulated_annealing
from thoi.heuristics.simulated_annealing_multi_order import simulated_annealing_multi_order
from argparse import ArgumentParser
from pathlib import Path

def hot_encoded_2_indices(hot_encoded: np.ndarray) -> list[int]:
    return list(np.where(hot_encoded == 1)[0])

def run_sa(X: np.ndarray, order: int, repeat: int, largest: bool):
    if order == -1:
        nplets, scores = simulated_annealing_multi_order(X, repeat=repeat, metric='o', largest=largest)
        nplets = [hot_encoded_2_indices(nplet) for nplet in nplets.numpy()]
    else:
        nplets, scores = simulated_annealing(X, order=order, repeat=repeat, metric='o', largest=largest)

    return nplets, scores

def generate_data(covmat: np.ndarray, T: int = 1000000) -> np.ndarray:
    N = len(covmat)
    return np.random.multivariate_normal(np.zeros(N), covmat, size=T)

def run_simulated_annealing(X: np.ndarray, orders_k: list[int]):

    # Running annealing    
    sa_repeat = 100
    sa_max_scores_k = np.zeros((len(orders_k)))
    sa_min_scores_k = np.zeros((len(orders_k)))
    sa_max_nplets_k = list()
    sa_min_nplets_k = list()

    for i, k in enumerate(tqdm(orders_k, desc='Order', leave=False)):

        # Maximizing
        max_nplets, max_scores = run_sa(X, order=k, repeat=sa_repeat, largest=True)
        max_vals_k_id = np.argmax(max_scores)
        sa_max_nplets_k.append(max_nplets[max_vals_k_id])
        sa_max_scores_k[i] = max_scores[max_vals_k_id]

        # Minimizing
        min_nplets, min_scores = run_sa(X, order=k, repeat=sa_repeat, largest=False)
        min_vals_k_id = np.argmin(min_scores)
        sa_min_nplets_k.append(min_nplets[min_vals_k_id])
        sa_min_scores_k[i] = min_scores[min_vals_k_id]

    return (
        (sa_max_scores_k, sa_max_nplets_k),
        (sa_min_scores_k, sa_min_nplets_k)
    )


def repeated_run_sa(X: np.ndarray, orders_k: list[int], n_repeats: int):

    N = X.shape[1]
    n_ks = len(orders_k)
    max_score_dist = np.zeros((n_ks, n_repeats))
    min_score_dist = np.zeros((n_ks, n_repeats))
    max_selected_variables = np.zeros((n_ks, N))
    min_selected_variables = np.zeros((n_ks, N))

    for repeat_id in tqdm(range(n_repeats), desc='Repeat SA', leave=False):
        (sa_max_scores_k, sa_max_nplets_k), (sa_min_scores_k, sa_min_nplets_k) = run_simulated_annealing(X, orders_k)

        for k_id in range(n_ks):
            max_score_dist[k_id, repeat_id] = sa_max_scores_k[k_id]
            min_score_dist[k_id, repeat_id] = sa_min_scores_k[k_id]
            max_selected_variables[k_id, sa_max_nplets_k[k_id]] += 1
            min_selected_variables[k_id, sa_min_nplets_k[k_id]] += 1
    
    return (
        max_score_dist,
        min_score_dist,
        max_selected_variables,
        min_selected_variables
    )

def main(path_to_data: Path, orders_k: list[int], n_repeats: int, output_path: Path):
    # Load data
    covmat = np.load(path_to_data)
    X = generate_data(covmat)

    # Run repeated simulated annealing
    results = repeated_run_sa(X, orders_k, n_repeats)

    # store results to result folder
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(output_path, *results)

if __name__ == "__main__":
    args = ArgumentParser(description="Run simulated annealing stability analysis.")
    args.add_argument(
        "--data_path",
        type=Path,
        required=True,
        help="Path to the input data file (numpy format)."
    )
    args.add_argument(
        "--orders_k",
        type=int,
        nargs='+',
        required=True,
        help="List of orders k to evaluate."
    )
    args.add_argument(
        "--n_repeats",
        type=int,
        default=10,
        help="Number of repeats for simulated annealing."
    )
    args.add_argument(
        "--output_path",
        type=Path,
        required=True,
        help="Path to save the output results (numpy format)."
    )
    parsed_args = args.parse_args()
    main(
        path_to_data=parsed_args.data_path,
        orders_k=parsed_args.orders_k,
        n_repeats=parsed_args.n_repeats,
        output_path=parsed_args.output_path
    )