import numpy as np


def feedback_driven_tensor_factorization(student_performance, n_concepts=2,
                                         mu=0.1, init=3, max_iter=100):
    """ Student performance: 0 if incorrect, 1 if correct or None if not
    observed """

    # Get values from student performance tensor shape
    n_students, n_questions, n_attempts = student_performance.shape

    # To not change original matrix
    student_performance = student_performance.copy()

    # Construct tensor X denoting when a student has or has not chosen to work
    # on a problem
    X = np.ones(student_performance.shape)
    X[np.where(np.isnan(student_performance))] = 0
    # Complete student knowledge tensor with zero where is NaN
    student_performance[np.where(np.isnan(student_performance))] = 0

    # Create student knowledge tensor
    student_knowledge = np.zeros((n_students, n_concepts, n_attempts))

    best_error = 9999
    lambda1 = 0.0001

    # Several starts
    for run in range(init):
        # Start with random Q-Matrix
        q_matrix = np.random.rand(n_concepts, n_questions)
        # Impose non-negativity constraint
        q_matrix[q_matrix <= 0] = 0.0001
        # Normalize rows to sum one
        row_sums = q_matrix.sum(axis=0, keepdims=True)
        if not (np.any(q_matrix.sum(axis=0))):
            raise RuntimeError("Q Matrix with empty row")
        q_matrix = q_matrix / row_sums

        student_performance_pred = np.zeros(student_performance.shape)
        for i in range(max_iter):
            # Phase 2: learning
            # Update T: T = 2*(T_{t-1}) + 2*((1-T_{t-1})/(1+exp(-mu*X_{t}*Q'))) - 1
            # For T0 user T-1 as 0
            student_knowledge[:, :, 0] = (2/(1+np.exp(
                -mu*np.dot(X[:, :, 0], q_matrix.T))))-1
            for attempt in range(1, n_attempts):
                student_knowledge[:, :, attempt] = (2*student_knowledge[
                    :, :, attempt-1]) + \
                    2*(1-student_knowledge[:, :, attempt-1])/(1+np.exp(
                        -mu*np.dot(X[:, :, attempt], q_matrix.T))) - 1

            # Phase 1: prediction
            # Update Q: Q = (T'T)^(-1)T'Y = T^(-1)Y
            # (T'T)^(-1)
            student_knowledge_transposed = np.zeros((n_concepts, n_concepts,
                                                     n_attempts))
            # TODO: make proper dot operation by transposing 2nd and 3rd
            # dimensions
            for attempt in range(n_attempts):
                student_knowledge_transposed[:, :, attempt] = np.dot(
                    student_knowledge[:, :, attempt].T, student_knowledge[
                        :, :, attempt])

            student_knowledge_transposed = student_knowledge_transposed.sum(
                axis=2)
            student_knowledge_transposed_inv = np.linalg.pinv(
                student_knowledge_transposed+lambda1)

            # T'Y
            TY = np.zeros((n_concepts, n_questions, n_attempts))
            for attempt in range(n_attempts):
                TY[:, :, attempt] = np.dot(student_knowledge[:, :, attempt].T,
                                           student_performance[:, :, attempt])
            TY = TY.sum(axis=2)

            # Q = (T'T)^(-1)T'Y
            q_matrix = np.dot(student_knowledge_transposed_inv, TY)
            # Impose non-negativity constraint
            q_matrix[q_matrix <= 0] = 0.0001
            # Normalize rows to sum one
            row_sums = q_matrix.sum(axis=0, keepdims=True)
            if not (np.all(row_sums)):
                # Should not be possible, something went wrong.
                # Skip this round.
                print("Q Matrix with empty row")
                break
                # raise RuntimeError("Q Matrix with empty row")
            q_matrix = q_matrix / row_sums

            # Y = TQ
            for attempt in range(n_attempts):
                student_performance_pred[:, :, attempt] = np.dot(
                    student_knowledge[:, :, attempt], q_matrix)

            # Calculate error
            diff = np.zeros((n_students, n_questions, n_attempts))
            for attempt in range(n_attempts):
                diff[:, :, attempt] = student_performance[:, :, attempt] - \
                    student_performance_pred[:, :, attempt]
            # Frobenius norm (norm-2)
            error = np.sqrt(np.sum(np.power(diff, 2)))
            if error < best_error:
                best_student_performance_pred = student_performance_pred.copy()
                best_student_knowledge = student_knowledge.copy()
                best_q_matrix = q_matrix.copy()
                best_error = error

    # if best_error == 9999:
        # raise RuntimeError("Could not converge")
    return (best_student_performance_pred, best_student_knowledge,
            best_q_matrix, best_error)
