from __future__ import annotations

import numpy as np


def response_matrix(truth_bins: np.ndarray, reco_bins: np.ndarray, n_truth: int, n_reco: int, weights: np.ndarray | None = None) -> np.ndarray:
    truth_bins, reco_bins = np.asarray(truth_bins, int), np.asarray(reco_bins, int)
    if truth_bins.shape != reco_bins.shape:
        raise ValueError("truth and reconstructed bin arrays must have equal shape")
    w = np.ones(len(truth_bins)) if weights is None else np.asarray(weights, float)
    matrix = np.zeros((n_reco, n_truth), float)
    for t, r, weight in zip(truth_bins, reco_bins, w):
        if 0 <= t < n_truth and 0 <= r < n_reco:
            matrix[r, t] += weight
    column_sums = matrix.sum(axis=0)
    return np.divide(matrix, column_sums[None, :], out=np.zeros_like(matrix), where=column_sums[None, :] > 0)


def iterative_bayes_unfold(measured: np.ndarray, response: np.ndarray, prior: np.ndarray | None = None, iterations: int = 4, efficiencies: np.ndarray | None = None) -> np.ndarray:
    measured, response = np.asarray(measured, float), np.asarray(response, float)
    n_truth = response.shape[1]
    prior = np.ones(n_truth) / n_truth if prior is None else np.asarray(prior, float)
    prior = prior / prior.sum()
    efficiencies = response.sum(axis=0) if efficiencies is None else np.asarray(efficiencies, float)
    unfolded = prior.copy()
    for _ in range(iterations):
        denominator = response @ prior
        bayes = np.divide(response * prior[None, :], denominator[:, None], out=np.zeros_like(response), where=denominator[:, None] > 0)
        unfolded = np.divide(bayes.T @ measured, efficiencies, out=np.zeros(n_truth), where=efficiencies > 0)
        total = unfolded.sum()
        if total > 0:
            prior = unfolded / total
    return unfolded


def tikhonov_unfold(measured: np.ndarray, response: np.ndarray, covariance: np.ndarray | None = None, regularization: float = 1e-8, derivative_order: int = 2) -> tuple[np.ndarray, np.ndarray]:
    y, r = np.asarray(measured, float), np.asarray(response, float)
    covariance = np.diag(np.maximum(y, 1.0)) if covariance is None else np.asarray(covariance, float)
    inverse = np.linalg.pinv(covariance, hermitian=True)
    n = r.shape[1]
    if derivative_order == 0:
        l = np.eye(n)
    else:
        l = np.diff(np.eye(n), n=derivative_order, axis=0)
    hessian = r.T @ inverse @ r + regularization * (l.T @ l)
    solution_covariance = np.linalg.pinv(hessian, hermitian=True)
    solution = solution_covariance @ r.T @ inverse @ y
    return solution, solution_covariance
