########################################################################
# Date: June 2015
# Author: Edward Johns (e.johns@imperial.ac.uk)
# This code may be freely distributed, but citations should be made to:
# E. Johns et al, "Becoming the Expert - Interactive Multi-Class Machine Teaching", in Proceedings of CVPR 2015
########################################################################

# Helpers
import numpy as np

def get_next_sample(X, Y, W, L):

    # Based on "Zhu et al., Combining Active Learning and Semi-Supervised Learning Using Gaussian Fields and Harmonic Functions, in ICML workshop 2003"

    # Input:
    # Below, nS = total number of samples, nC = number of classes, nL = number of observed samples, nT = total number of testing samples to be shown to user
    # X: nS*nC belief matrix, with each row representing one sample, and each column representing one column. Each element is the probability that the user thinks that sample is assigned to that class. This would be identical to Y if we were assuming that the user always assigns the ground truth to an observed sample, and never has memory fall-off.
    # Y: nS*nC ground truth matrix (NumPy array), with each row in indicator encoding. This represents the ground-truth labels of all points. As such, each row has only one "1" and all other entries are "0".
    # W: nS*nS graph weights matrix (symmetrical NumPy array), with each row and each column corresponding to one sample. Each element is the weight (affinity) between two samples.
    # L: nL*1 labeled set, where each element is one sample that has already been shown to the user, with indices between 1 and nS.
    # Output:
    #    next_sample: the index of the optimum sample to be shown next, as selected by the active teaching algorithm.

    # Get the total number of samples (nS) and total number of classes (nC). nC is not actually used.
    [nS, nC] = X.shape

    # Create the set of unlabelled samples (U)
    U = np.setdiff1d(np.arange(nS), L)

    # Get the number of unlabelled samples (nU)
    nU = len(U)

    # Get the ground truth for the unlabelled samples
    Yu = Y.take(U, 0)

    # Get the unlabelled section of the covariance matrix
    Delta = np.subtract(np.diag(np.sum(W, 1)), W)
    ## To understand the take functions
    ## Delta.take(U,0) = Delta[U,:]
    ## Delta.take(U,1) = Delta[:,U]
    ## Delta.take(U, 0).take(U, 1) = Delta[U,:][:, U]
    ## It filters for every unlabeled row, the unlabeled columns.
    invDeltaU = np.linalg.inv(Delta.take(U, 0).take(U, 1))

    # Get the current state of the GRF, for the unlabeled samples
    ## W[U, :][:,L] = W.take(U, 0).take(L, 1)
    ## X[L, :] = X.take(L, 0)
    ## Why W and not Delta?? Delta is the negative of W for indices that are not ii.
    ## Not sure why original implementation chose W and not Delta
#     f = np.dot(invDeltaU, np.dot(W.take(U, 0).take(L, 1), X.take(L, 0)))
#     print(f)
    # Mean value of the unlabeled data points
    f = np.dot(-invDeltaU, np.dot(Delta.take(U, 0).take(L, 1), X.take(L, 0)))

    # Create a list of risks, one for each unlabelled sample
    uRisks = np.zeros(nU)

    # Try each unlabelled sample
    for u in range(nU):
        # Find the sample number (remember that U is just the list of unlabelled samples, not all the samples)
        s = U[u]

        # Calculate the new state of the GRF if this sample were to be revealed to the user (here, we assume
        # that the user's belief of this sample will then be the ground truth -- debatable...)
        GG = invDeltaU[:, u] / invDeltaU[u, u]
        diff = Y[s, :] - f[u, :]
        fPlus = f + np.dot(GG[..., np.newaxis], diff[np.newaxis, ...])

        # Sum up the risks over all unlabelled points (i.e. the difference between the new state, and the
        # ground truth)
#         D = np.abs(1 - fPlus[Yu == 1])
        # Don't understand why the need of ABS. Maybe because it was negative when using W and not Delta?
        D = 1 - fPlus[Yu == 1]
        uRisks[u] = np.sum(D)

    # Get the sample which minimised the risk
    next_sample_index = np.argmin(uRisks)
    next_sample = U[next_sample_index]

    # Return this sample
    return next_sample
