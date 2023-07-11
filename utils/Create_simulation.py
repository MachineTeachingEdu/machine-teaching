import numpy as np
import pandas as pd
import pickle as pk
import matplotlib.pyplot as plt

def simulated_data(n, a, q, e, c, num_view, datatype = None):
    ''' create simulated data
        n as number of student,
        a as number of attempt,
        p as number of problem,
        q as number of question,
        c as number of concept'''

    # create matrix for q and e
    quiz_concept = np.random.uniform(0,1, [c, q])
    example_concept = np.random.uniform(0,1, [c, e])

    sumq = sum(quiz_concept)
    sume = sum(example_concept)

    quiz_concept = quiz_concept/sumq # normalized q and e
    example_concept = example_concept/sume

    # random create student activity sequence
    sequence_matrix = np.zeros([n,a])
    if num_view == 1:
        for i in range(0, n):
            sequence_matrix[i, :] = np.random.choice(range(0, q), a)
    else:
        for i in range(0,n):
            sequence_matrix[i,:] = np.random.choice(range(0,q+e),a)

    # create tensor t
    t = np.random.normal(0,1, [n, a, c]) # randomly create a tensor
    t1 = np.random.uniform(0,0.3, [n,c])   # create first slice of tensor as the student ability
    t[:, 0, :] = np.copy(t1)

    for i in range(1, a): #according to
        temp = np.copy(t1)
        for s in range(0,n):
            forgetornot = np.random.uniform(0,1) # probability for random forget
            if forgetornot >= 0.5: # if probability >= 0.5, then forget the knowledge instead of learning knowledge
                random_forget = np.random.uniform(0,0.05,c)
                temp[s, :] =  temp[s,:] - random_forget
                temp[s, :][temp[s,:] < 0] = 0
            else: # if not forget, then random increase the knowledge based on the question
                qestion = int(sequence_matrix[s, i])
                if qestion < q:
                    temp[s,:] = t1[s,:] + np.multiply(quiz_concept[:,qestion], np.random.uniform(0, 0.8, c))
                else:
                    temp[s, :] = t1[s, :] + np.multiply(example_concept[:, qestion-q], np.random.uniform(0, 0.8, c))
        t[:,i,:] = np.copy(temp)
        t1 = np.copy(temp)

    # quiz transpose, so that the shape of quiz and example be the [student, quiz, score]
    quiz = np.transpose(np.dot(t, quiz_concept), (0, 2, 1))
    example = np.transpose(np.dot(t, example_concept), (0, 2, 1))

    final_q = np.zeros([n,q,a])
    final_e = np.zeros([n,e,a])
    for i in range(0,n):
        for j in range(0,a):
            activty = int(sequence_matrix[i,j])
            if activty < q:
                final_q[i,activty,j] = np.copy(quiz[i,activty,j])

    for i in range(0,n):
        for j in range(0,a):
            activty = int(sequence_matrix[i,j])
            if activty >= q:
                activty = activty - q
                if datatype == 'Quiz_Discussion': # if the learning resource want to create is binary, then make example to be binary
                    final_e[i, activty, j] = 1
                else:
                    final_e[i,activty,j] = np.copy(example[i,activty,j])
    return final_q, final_e, t, quiz_concept, example_concept



def simulated_data_STQ(n, a, q, e, c, k, num_view, datatype = None):
    ''' create simulated data STQ
        n as number of student,
        a as number of attempt,
        p as number of problem,
        q as number of question,
        c as number of concept
        k as number of latent student feature'''

    # create matrix for q and e
    quiz_concept = np.random.uniform(0,1, [c, q])
    example_concept = np.random.uniform(0,1, [c, e])

    sumq = sum(quiz_concept)
    sume = sum(example_concept)

    quiz_concept = quiz_concept/sumq # normalized q and e
    example_concept = example_concept/sume

    # create matrix for s
    latent_S = np.random.uniform(0, 1, [n, k])

    # random create student activity sequence
    sequence_matrix = np.zeros([n,a])
    if num_view == 1:
        for i in range(0, n):
            sequence_matrix[i, :] = np.random.choice(range(0, q), a)
    else:
        for i in range(0,n):
            sequence_matrix[i,:] = np.random.choice(range(0,q+e),a)

    # create tensor t
    t = np.random.normal(0,1, [k, a, c]) # randomly create a tensor
    t1 = np.random.uniform(0, 0.05, [k,c])   # create first slice of tensor as the student ability
    t[:, 0, :] = np.copy(t1)


    for i in range(1, a): #according to
        temp = np.copy(t1)
        for s in range(0,n):
            forgetornot = np.random.uniform(0,1) # probability for random forget
            if forgetornot >= 0.7: # if probability >= 0.5, then forget the knowledge instead of learning knowledge
                random_forget = np.random.uniform(0,0.1,c)
                temp =  temp - random_forget
                temp[temp < 0] = 0
            else: # if not forget, then random increase the knowledge based on the question
                qestion = int(sequence_matrix[s, i])
                if qestion < q:
                    temp = t1 + np.multiply(np.outer(latent_S[s, :], quiz_concept[:, qestion]), np.random.uniform(0, 0.4, c))
                else:
                    temp = t1 + np.multiply(np.outer(latent_S[s, :], example_concept[:, qestion-q]), np.random.uniform(0, 0.4, c))
        t[:,i,:] = np.copy(temp)
        t1 = np.copy(temp)

    # quiz transpose, so that the shape of quiz and example be the [student, quiz, score]
    quiz = latent_S.dot(np.transpose(np.dot(t, quiz_concept), (2, 0, 1)))
    example = latent_S.dot(np.transpose(np.dot(t, example_concept), (2, 0, 1)))

    for i in range(0,n):
        quiz[i,:,:] = quiz[i,:,:] + student_bias[i]
        example[i, :, :] = example[i, :, :] + student_bias[i]

    # remove none observation
    final_q = np.zeros([n,q,a])
    final_e = np.zeros([n,e,a])
    for i in range(0,n):
        for j in range(0,a):
            activty = int(sequence_matrix[i,j])
            if activty < q:
                final_q[i,activty,j] = np.copy(quiz[i,activty,j])

    for i in range(0,n):
        for j in range(0,a):
            activty = int(sequence_matrix[i,j])
            if activty >= q:
                activty = activty - q
                if 'Quiz_Discussion_STQ' in data_type: # if the learning resource want to create is binary, then make example to be binary
                    final_e[i, activty, j] = 1
                else:
                    final_e[i,activty,j] = np.copy(example[i,activty,j])
    return final_q, final_e, t, quiz_concept, example_concept


if __name__ == '__main__':
    n = 1000      #n as number of student
    a = 20        #a as number of attempt
    q = 10      #p as number of problem
    e = 15       #q as number of question
    c = 3       #c as number of concept
    k = 3       #k as number of latent student feature
    # data_type = 'Quiz_Assignment' #simulation data type, assignment(continous) or discussion(binary)
    # data_type = 'Quiz_Discussion'
    # data_type = 'Quiz_Discussion_STQ'
    data_type = 'Quiz_Discussion_STQ_Thresholded'
    # data_type = 'Quiz_Only'
    # data_type = 'Quiz_Only_Discussion_STQ'
    # num_view = 1
    num_view = 2


    # quiz, example, t, quiz_concept, example_concept = simulated_data(n, a, q, e, c,num_view, data_type)
    quiz, example, t, quiz_concept, example_concept = simulated_data_STQ(n, a, q, e, c, k, num_view, data_type)


    quiz_score_bf = []
    for i in range(0, n):
        for j in range(0, q):
            for k in range(0, a):
                # print i, j, k
                # print quiz[i,j,k]
                if quiz[i, j, k] != 0:
                    quiz_score_bf.append(quiz[i, j, k])

    plt.hist(quiz_score_bf)
    plt.show()

    quiz[quiz > 1] = 1


    quiz_score = []
    for i in range(0, n):
        for j in range(0, q):
            for k in range(0, a):
                # print i, j, k
                # print quiz[i,j,k]
                if quiz[i, j, k] != 0:
                    quiz_score.append(quiz[i,j,k])

    plt.hist(quiz_score)
    plt.show()


    # save non accumulative simulation data
    with open('data_redo/simulated_data/{}/simulated_data.txt'.format(data_type), 'w') as f:
        for i in range(0,n):
            for j in range(0,q):
                for k in range(0,a):
                    # print i, j, k
                    # print quiz[i,j,k]
                    if quiz[i,j,k] != 0:
                        f.writelines('{},{},{},{},{}\n'.format(i,j,quiz[i,j,k],k,0))
        for i in range(0,n):
            for j in range(0,e):
                for k in range(0,a):
                    # print i, j, k
                    # print quiz[i,j,k]
                    if example[i,j,k] != 0:
                        f.writelines('{},{},{},{},{}\n'.format(i,j,example[i,j,k],k,1))



    #save simulated t, q and e
    tt = {'t': t}
    with open('data_redo/simulated_data/{}/simulated_T.pkl'.format(data_type),
              'wb') as f:
        pk.dump(tt, f)

    qq = {'q': quiz_concept}
    with open('data_redo/simulated_data/{}/simulated_Q.pkl'.format(data_type),
              'wb') as f:
        pk.dump(qq, f)

    ee = {'e': example_concept}
    with open('data_redo/simulated_data/{}/simulated_E.pkl'.format(data_type),
              'wb') as f:
        pk.dump(ee, f)