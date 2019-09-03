# DB
from questions.models import Solution, Problem
import psycopg2

# Helpers
# import numpy as np
import pickle
import base64

# Preprocessing
from tokenizer import create_bag_of_words
from sklearn.feature_extraction.text import CountVectorizer


class RetrieveModelAndVectorizer(object):
    """ Recreate vectorizer and load saved model from DB """
    def __init__(self):
        self.connect()

    def connect(self):
        """ Connect to DB """
        connection = psycopg2.connect(user="machineteaching",
                                      password="",
                                      host="localhost",
                                      database="machineteaching")
        connection.autocommit = True
        self.cursor = connection.cursor()

    def get_original_solutions(self):
        # Cleaning database
        last_id = 132
        problems = Problem.objects.filter(id__gt=last_id)
        solutions_obj = Solution.objects.filter(
            problem__in=problems).update(ignore=True)
        print("Problems to be ignored: %d" % problems.count())

        problems = Problem.objects.filter(id__lte=last_id)
        # problems = Problem.objects.all()
        print("Problems to be used: %d" % problems.count())

        solutions_obj = Solution.objects.filter(
            problem__in=problems, ignore=False).order_by('id')
        # solutions_obj = Solution.objects.all().order_by('id')
        print("Solutions to be used: %d" % solutions_obj.count())

        # docs_id = []
        # questions = []
        solutions = []

        # Fill separated structures
        for sol in solutions_obj:
            # docs_id.append(sol.id)
            # questions.append(sol.problem.content)
            solutions.append(sol.content)

        print("Got %d documents" % (solutions_obj.count()))
        return solutions

    def get_where_items(self, exp_id):
        """ Get where clause for experiment """
        cols = ["vectorizer", "min_df", "is_binary", "distance",
                "method", "dataset", "k", "model", "X"]
        query = "SELECT %s from experiments_solution where experiment_id = %s" % (
                ", ".join(cols), exp_id)
        self.cursor.execute(query)
        where_items = self.cursor.fetchall()
        return where_items

    def recreate_vectorizer(self, solutions, where_items, exp_id):
        """ Recreate vectorizer from where clause conditions """
        v = eval(where_items[0][0])
        m = where_items[0][1]
        b = where_items[0][2]
        # dist = where_items[0][3]
        # method = where_items[0][4]
        # k = where_items[0][6]
        # model_db = pickle.loads(base64.b64decode(where_items[0][7]))
        # X = np.asarray(where_items[0][8])

        train_data_features, vectorizer, feature_names = create_bag_of_words(
            solutions, v, binary=b, min_df=m)

        return vectorizer

    def get_model_and_vectorizer(self, exp_id):
        """ Recreate vectorizer and load saved model from database """
        # Recreate vectorizer
        where_items = self.get_where_items(exp_id)
        solutions = self.get_original_solutions()
        self.vectorizer = self.recreate_vectorizer(
            solutions, where_items, exp_id)

        # Load saved model
        self.model_db = pickle.loads(base64.b64decode(where_items[0][7]))
        self.model_db.n_jobs = 1

        return self.vectorizer, self.model_db
