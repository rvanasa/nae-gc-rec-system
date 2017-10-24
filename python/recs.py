import pandas as pd
import numpy as np
import sqlite3
import spacy


class Recsystem:

    """
    Recsystem(BASE, username)

    Recommendation system (draft) class. Contains methods needed to
    preprocess data and process responses to user input.

    Parameters
    ----------
    BASE : string
        The absolute directory where the Allen AI CSV files are stored.

    test_type : string
        The username of the user accessing the api

    Attributes
    ----------
    base : string
        contains BASE as a class variable

    df : pandas Dataframe
        contains preprocessed CSV data of questions, responses, and auxilary data about each question

    grade_range : int
        contains the number of grades the data spans over. In this dataset, `grade_range` is 7.

    grade : int
        contains user-entered grade as a class variable

    last_percentage : float
        Once a user has responded to a question, `last_percentage` contains the percentage of students
        who answered correctly to the question the user just responded to.

    qs_answered : int
        The total number of questions the user has answered during a session.

    percentage : float
        The percentage of answered questions the user has answered correctly

    last_question : string
        Once a user has responded to a question, `last_question` contains the exact question the
        user has just responded to.

    A : string
        The answer corresponding to option A (or 1 on select tests)

    B : string
        The answer corresponding to option B (or 2 on select tests)

    C : string
        The answer corresponding to option C (or 3 on select tests)

    D : string
        The answer corresponding to option D (or 4 on select tests)

    test_type : string
        Contains user-entered test_type as a class variable.

    answered_questions : List of strings
        contains the questionIDs of the questions the user has answered previously.

    index : int
        The index in the dataframe of the questoin the user has just responded to. Once updated
        through the `updates()` function, it will contain the index of the question the user will
        respond to.

    Methods
    -------
    prep_next_q(answer)
        Ranks all questions by a similarity function then determines which question is most similar that the
        user has not answered. Then picks the index of the most similar question, and updates class variables
        accordingly.

    send_question()
        Sends the question and four answers in a format printable by the user. Currently a stub method- will
        probably have to convert Q + answer into JSON in this function.

    send_user_stats()
        Sends the variable user stats- such as percentage correct and number of questions answered

    send_q_stats()
        Sends statistics about the question, including what percent of students
        got it right in the user's grade category

    update_sql()
        Sends user information that has been updated after each question to the database

    Reads
    -----
    questions : sql table
        Contains `self.df` in SQL table form. Used to store preprocessed data.

    users : sql table
        Contains user variable info for each user. Some sections are mutable, unlike
        `questions` which is generally immutable

    """

    def __init__(self, BASE):

        # Define dataset of questions
        self.base = BASE

        # Define word tokenizer
        self.nlp = spacy.load('en')

        # Define static values of dataset
        self.grade_range = 7  # grades 3 - 9 inclusive
        self.min_grade = 3
        self.max_grade = 9
        self.all_test_types = ['ACTAAP', 'AIMS', 'Louisiana Educational Assessment Program',
                               'MCAS', 'MEA', 'MSA', 'TIMSS', 'WASL',
                               'Alaska Department of Education and Early Development',
                               'California Standards Test', 'FCAT', 'Maryland School Assessment',
                               'MEAP', 'NAEP', 'North Carolina READY End-of-Grade Assessment',
                               'NYSEDREGENTS', 'Ohio Achievement Tests', 'TAKS',
                               'Virginia Standards of Learning - Science', 'AMP']

        # Preprocess dataset and read into sql if not done already
        self.conn = sqlite3.connect('recs.db')
        self.c = self.conn.cursor()
        self.c.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        tables = self.c.fetchall()[0][0]
        if tables < 2:
            self.df = self._preprocess_data()
        self.df = pd.read_sql('SELECT * FROM questions;', self.conn)

        # Define question and response
        self.last_question = ""
        self.A = ""
        self.B = ""
        self.C = ""
        self.D = ""
        self.q_grade = -1

        # Define user vars
        self.last_percentage = 0

        # Define empty user vars
        self.username = None
        self.grade = None
        self.qs_answered = None
        self.percentage = None
        self.test_type = None
        self.answered_questions = None

        # Define temporary variable index- which question currently being answered
        # index is initially a random question that the user has not answered
        self.index = None

        self.conn.close()

    def init_user(self, username):
        self.conn = sqlite3.connect('recs.db')
        self.c = self.conn.cursor()
        self.username = username
        try:
            user = pd.read_sql('SELECT * FROM users WHERE username=' + '"' + self.username + '";', self.conn)
        except pd.io.sql.DatabaseError:
            raise ValueError("Username NOT found")

        # Define user variables
        self.grade = int(user['grade'][0])
        self.qs_answered = int(user['qs_answered'][0])
        self.percentage = float(user['percentage'][0])
        self.test_type = user['test_type'][0]
        if user['answered_questions'][0] == '[]':
            self.answered_questions = []
        else:
            self.answered_questions = user['answered_questions'][0].split('____')

        self.index = np.random.randint(0, self.df.shape[0])
        while self.df.iloc[[self.index]]['question']._values[0] in self.answered_questions:
            self.index = np.random.randint(0, self.df.shape[0])
        self._update_by_index()

        self.conn.close()

    def _preprocess_data(self):

        # Read CSVs from dataset
        df1 = pd.read_csv(self.base + '/ElementarySchool/Elementary-NDMC-Train.csv')
        df2 = pd.read_csv(self.base + '/ElementarySchool/Elementary-NDMC-Test.csv')
        df3 = pd.read_csv(self.base + '/ElementarySchool/Elementary-NDMC-Dev.csv')

        df4 = pd.read_csv(self.base + '/MiddleSchool/Middle-NDMC-Train.csv')
        df5 = pd.read_csv(self.base + '/MiddleSchool/Middle-NDMC-Test.csv')
        df6 = pd.read_csv(self.base + '/MiddleSchool/Middle-NDMC-Dev.csv')

        df = pd.concat([df1, df2, df3, df4, df5, df6])
        del df['subject']
        del df['category']

        # Remove all diagram questions and free responses
        df = df[df.isMultipleChoiceQuestion == 1]
        df = df[df.includesDiagram == 0]

        # 1)) Data preprocessing- we must standardize some of the test names
        df.loc[df.examName == 'California Standards Test - Science', 'examName'] = 'California Standards Test'
        df.loc[df.examName == 'Maryland School Assessment - Science', 'examName'] = 'Maryland School Assessment'
        df.loc[df.examName == 'Alaska Department of Education & Early Development',
               'examName'] = 'Alaska Department of Education and Early Development'
        df.loc[df.examName == 'Alaska Dept. of Education & Early Development',
               'examName'] = 'Alaska Department of Education and Early Development'

        # 2)) we split each question to question and answers
        df7 = df.apply(lambda row: self._answers(row['question'], row['questionID']), axis=1)
        del df['question']
        df = df.merge(df7)


        # 3)) We create a toy distribution for each question based on the grade the question was assigned
        dist_df = df.apply(lambda row: self._correct(row['schoolGrade'], row['questionID']), axis=1)
        df = df.merge(dist_df)
        df['questionID'] = df['questionID'].str.decode('utf-8')
        df['originalQuestionID'] = df['originalQuestionID'].str.decode('utf-8')
        df['AnswerKey'] = df['AnswerKey'].str.decode('utf-8')
        df['examName'] = df['examName'].str.decode('utf-8')
        df['year'] = df['year'].str.decode('utf-8')
        df['question'] = df['question'].str.decode('utf-8')
        df['A'] = df['A'].str.decode('utf-8')
        df['B'] = df['B'].str.decode('utf-8')
        df['C'] = df['C'].str.decode('utf-8')
        df['D'] = df['D'].str.decode('utf-8')

        df.head()

        df.to_sql("questions", self.conn, if_exists="replace")

    def _answers(self, qs, id):

        def split_answer(qs, letter):
            response = []
            split_letter = '(' + letter + ')'
            splits = qs.split(split_letter)
            if len(splits) > 1:
                response = splits[1]
                qs = splits[0]
            return response, qs

        D, qs = split_answer(qs, 'D')
        C, qs = split_answer(qs, 'C')
        B, qs = split_answer(qs, 'B')
        A, qs = split_answer(qs, 'A')

        if len(A) == 0:
            D, qs = split_answer(qs, '4')
            C, qs = split_answer(qs, '3')
            B, qs = split_answer(qs, '2')
            A, qs = split_answer(qs, '1')

        A = "A. " + A.strip()
        B = "B. " + B.strip()
        C = "C. " + C.strip()
        if isinstance(D, str):
            D = "D. " + D.strip()

        return pd.Series({"questionID": id, "question":qs, "A": A, "B": B, "C":C, "D":D})

    # 3)) We create toy distributions of student responses by grade
    def _correct(self, q_grade, id):
        grade = int(q_grade)
        qs_answered = np.random.randint(1, 501, self.grade_range) # students in each grade who answered question

        # First we get a random mean between [10, 95]
        mu = 75*np.random.rand() + 20

        # Then we get a random standard deviation between [5, 20]
        sigma = 15*np.random.rand() + 5

        # Then we create a normal distribution, and take 7 random numbers, sort them
        # and return them as probabilities
        probs = np.random.normal(mu, sigma, 1000)
        np.random.shuffle(probs)
        distribution = probs[0:self.grade_range]
        distribution = np.sort(distribution)

        # Then we generate random numbers for each grade- mu is the grade of q
        series = {}

        for n in range(0, self.grade_range):
            series[str(n + self.min_grade)] = distribution[n]
            series[str(n + self.min_grade) + '_users'] = qs_answered[n]
        series['questionID'] = id

        return pd.Series(series)

    def _match_profile(self, row):

        # we scale each individual score to be out of 100
        difference_score = 0.0

        # Compare grade
        grade_weight = 1
        q_grade = int(row['schoolGrade'])
        diff = q_grade - self.grade
        difference_score += (6 - diff) / float(6) * grade_weight

        # Compare percentage
        percentage_weight = 1
        q_percent = row[str(self.grade)]
        q_answers = row[str(self.grade) + "_users"]
        difference_last = 1 - abs(q_percent - self.last_percentage) * percentage_weight / float(100)
        difference_percent = 1 - abs(q_percent - self.percentage) * percentage_weight * self.qs_answered / float(100)
        difference_score = difference_last + difference_percent + difference_score

        # compare last question by token sort ratio
        q1 = self.nlp(self.last_question)
        q2 = self.nlp(row['question'])
        word_list_1 = []
        word_list_2 = []
        for word in q1:
            if word.pos_ == 'NOUN':
                word_list_1.append(word.text)

        for word in q2:
            if word.pos_ == 'NOUN':
                word_list_2.append(word.text)

        tokenized_q1 = " ".join(sorted(word_list_1))
        tokenized_q2 = " ".join(sorted(word_list_2))

        tk_q1 = self.nlp(tokenized_q1)

        # TypeError occurs if sentence has no nouns
        try:
            sim = tk_q1.similarity(self.nlp(tokenized_q2))
        except TypeError:
            sim = 0

        difference_q = 1 - sim
        question_weight = 100
        difference_score += question_weight * difference_q

        # Compare test type
        difference_test = 1
        if self.test_type == row['examName']:
            difference_test = 0
        test_weight = 1
        difference_score += difference_test * test_weight

        return difference_score

    # 5)) We implement a function to check if an answer is correct
    def _check_answer(self, answer):
        if self.df.iloc[[self.index]]['AnswerKey']._values[0] == answer:
            return True
        return False

    # 6)) We implement a function to find the minimum dissimilar that the user has not already answered
    def prep_next_q(self, answer):

        self._updates(answer)

        # Get similarity
        self.df['similarity'] = self.df.apply(lambda row: self._match_profile(row), axis=1)
        self.df = self.df.sort_values('similarity')

        # Find question based on similarity
        found_q = False
        n = 0
        while not found_q:
            if self.df.iloc[[n]]['questionID']._values[0] not in self.answered_questions:
                found_q = True
                self.index = n
            n += 1

        # Update class and db information
        self._update_by_index()
        self._update_sql()

    # 7)) We update student  / db statistics based on answered question
    def _updates(self, answer):

        correct = self._check_answer(answer)

        # Update percentage
        qs_right = int(self.percentage * self.qs_answered)
        if correct:
            qs_right += 1

        # Update qs answered
        self.qs_answered += 1
        self.percentage = qs_right / float(self.qs_answered)

        # Update db number in grade who answered + percentage correct
        prev_correct = int(self.df.at[self.index, str(self.grade)] * self.df.at[self.index, str(self.grade) + "_users"])
        if correct:
            prev_correct += 1
        self.df.at[self.index, str(self.grade) + "_users"] += 1
        self.df.at[self.index, str(self.grade)] = prev_correct

    # After picking a new question, we update our class variables accordingly
    def _update_by_index(self):

        # Update last percentage
        self.last_percentage = self.df.iloc[[self.index]][str(self.grade)]._values[0]

        # Update last question
        self.last_question = self.df.iloc[[self.index]]['question']._values[0]
        self.A = self.df.iloc[[self.index]]['A']._values[0]
        self.B = self.df.iloc[[self.index]]['B']._values[0]
        self.C = self.df.iloc[[self.index]]['C']._values[0]
        self.D = self.df.iloc[[self.index]]['D']._values[0]

        # Update question IDs
        self.answered_questions.append(self.df.iloc[[self.index]]['questionID']._values[0])

        # Update question grade
        self.q_grade = self.df.iloc[[self.index]]['schoolGrade']._values[0]

    def send_question(self):
        return self.last_question, self.A, self.B, self.C, self.D

    def send_user_stats(self):
        return self.percentage, self.qs_answered

    def send_q_stats(self):
        return self.last_percentage

    def _update_sql(self):
        self.conn = sqlite3.connect('recs.db')
        self.c = self.conn.cursor()

        sql_command = "UPDATE users SET grade="
        sql_command += str(self.grade)
        sql_command += ", qs_answered="
        sql_command += str(self.qs_answered)
        sql_command += ", percentage="
        sql_command += str(self.percentage)
        sql_command += ", answered_questions="
        sql_command += '"' + '____'.join(self.answered_questions) + '"'
        sql_command += " WHERE username="
        sql_command += '"' + self.username + '";'

        self.c.execute(sql_command)
        self.conn.commit()
        self.conn.close()

    # Ends sql connection
    def _end_session(self):
        self.conn.close()

