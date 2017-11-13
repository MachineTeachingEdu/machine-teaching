""" Class to create database with problems and solutions in Python """
import sqlite3
from sqlite3 import Error


class PythonProblems(object):
    def __init__(self, db_file, sql_file=None):
        """ initialize with database filename """
        self.db_file = db_file
        self.create_connection()
        if sql_file:
            self.create_tables(sql_file)

    def create_connection(self):
        """ create a database connection to the SQLite database
            specified by db_file
        """
        try:
            self.conn = sqlite3.connect(self.db_file)
            return self.conn
        except Error as e:
            print(e)

        return None

    def create_tables(self, create_table_sql):
        """ create a table from the create_table_sql statement
        :param create_table_sql: a file containing SQL statements
        return
        """
        try:
            c = self.conn.cursor()
            with open(create_table_sql, 'r') as sql_file:
                sql_command = sql_file.read()
            statements = sql_command.split(';')
            for statement in statements:
                c.execute(statement)
        except Error as e:
            print(e)

    def populate(self, rows):
        """
        Create a new project into the projects table
        :param rows: dict list containing table and column names in keys and respective values
        :return: list with ids
        """
        sql_template = ''' INSERT INTO %s(%s) VALUES(%s) '''
        total = 0
        idx_old = -1
        for item in rows:
            # Get problem and solution
            problem = item["problem"]
            solution = item["solution"]

            # If problem has not already been inserted (same problem,
            # different solutions), add problem
            idx_current = solution["idx"]
            if idx_current != idx_old:
                problem_sql = sql_template % ("problem", ','.join(problem.keys()),
                    ','.join(list('?'*len(problem.keys()))))
                cur = self.conn.cursor()
                cur.execute(sql, problem.values())
                problem_id = cur.lastrowid


            # Add problem
            solution["problem_id"] = problem_id
            del solution["idx"]
            solution_sql = sql_template % ("solution", ','.join(solution.keys()),
                    ','.join(list('?'*len(solution.keys()))))
            cur = self.conn.cursor()
            cur.execute(sql, problem.values())

            # Update control
            total += 1
            idx_old = idx_current

        return total
