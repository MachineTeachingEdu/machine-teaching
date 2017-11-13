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
        for item in rows:
            problem = item["problem"]
            solution = item["solution"]
            problem_sql = sql_template % ("problem", ','.join(problem.keys()),
                    ','.join(list('?'*len(problem.keys()))))
            cur = conn.cursor()
            cur.execute(sql, problem.values())
            solution["problem_id"] = cur.lastrowid
            solution_sql = sql_template % ("solution", ','.join(solution.keys()),
                    ','.join(list('?'*len(solution.keys()))))
            total += 1
        return total
