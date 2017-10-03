import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz


class Recsystem:

    """
    Recsystem(BASE, grade, test_type)

    Recommendation system (draft) class. Contains methods needed to
    preprocess data and process responses to user input.

    Parameters
    ----------
    BASE : string
        The absolute directory where the Allen AI CSV files are stored.

    grade : int
        The user's entered grade. Can be from grade 3 to 9 currently.

    test_type : string
        The test the user would like to study for ideally. While our
        system currently will give questions typically from outside of the
        exam, if two questions are equally weighted one being of the same test
        type will weight towards that specified by test_type.

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
    prep_next_q()
        Ranks all questions by a similarity function then determines which question is most similar that the
        user has not answered. Then picks the index of the most similar question, and updates class variables
        accordingly.

    send_question()
        Sends the question and four answers in a format printable by the user. Currently a stub method- will
        probably have to convert Q + answer into JSON in this function.


    """

    def __init__(self, BASE, grade, test_type):

        # Define dataset of questions
        self.base = BASE

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

        # Check grade and test_type
        if grade < 3 or grade > 9:
            raise ValueError("Grade level not supported")

        if test_type not in self.all_test_types:
            raise ValueError("Test type not supported")

        # Preprocess dataset
        self.df = self._preprocess_data()

        # Define user variables
        self.grade = grade
        self.last_percentage = 0.0
        self.qs_answered = 0
        self.percentage = 0.0
        self.test_type = test_type
        self.answered_questions = []

        # Define question and response
        self.last_question = ""
        self.A = ""
        self.B = ""
        self.C = ""
        self.D = ""

        # Define temporary variable index- which question currently being answered
        # index is initially set with a random value
        self.index = np.random.randint(0, self.df.shape[0])

    def _preprocess_data(self):

        # Read CSVs from dataset
        df1 = pd.read_csv(self.base + '\\ElementarySchool\\Elementary-NDMC-Train.csv')
        df2 = pd.read_csv(self.base + '\\ElementarySchool\\Elementary-NDMC-Test.csv')
        df3 = pd.read_csv(self.base + '\\ElementarySchool\\Elementary-NDMC-Dev.csv')

        df4 = pd.read_csv(self.base + '\\MiddleSchool\\Middle-NDMC-Train.csv')
        df5 = pd.read_csv(self.base + '\\MiddleSchool\\Middle-NDMC-Test.csv')
        df6 = pd.read_csv(self.base + '\\MiddleSchool\\Middle-NDMC-Dev.csv')

        df = pd.concat([df1, df2, df3, df4, df5, df6])

        # Remove all diagram questions and free responses
        df = df[df.isMultipleChoiceQuestion == 1]
        df = df[df.includesDiagram == 0]

        # 1)) Data preprocessing- we must standardize some of the test names
        df.examName[df.examName == 'California Standards Test - Science'] = 'California Standards Test'
        df.examName[df.examName == 'Maryland School Assessment - Science'] = 'Maryland School Assessment'
        df.examName[df.examName == 'Alaska Department of Education & Early Development'] = 'Alaska Department of Education and Early Development'
        df.examName[df.examName == 'Alaska Dept. of Education & Early Development'] = 'Alaska Department of Education and Early Development'

        # 2)) we split each question to question and answers
        df['question'] = df['question'].astype(str)
        df7 = df.apply(lambda row: self._answers(row['question'], row['questionID']), axis=1)
        del df['question']
        df = df.merge(df7)

        # 3)) We create a toy distribution for each question based on the grade the question was assigned
        dist_df = df.apply(lambda row: self._correct(row['schoolGrade'], row['questionID']), axis=1)
        df = df.merge(dist_df)

        return df

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

        return pd.Series({"questionID": id, "question":qs, "A": A, "B": B, "C":C, "D":D})

    # 3)) We create toy distributions of student responses by grade
    def _correct(self, id):
        grade = self.grade
        distribution = np.zeros(self.grade_range) # grades 3 - 9
        qs_answered = np.random.randint(1, 501, self.grade_range) # students in each grade who answered question

        # First we get a random mean between [10, 95]
        mu = 85*np.random.rand() + 10

        # Then we get a random standard deviation between [5, 20]
        sigma = 15*np.random.rand() + 5

        # Then we generate random numbers for each grade- mu is the grade of q
        series = {}
        for n in range(0, self.grade_range):
            if n + self.min_grade == grade:
                distribution[n] = mu
            else:
                found_num = False
                while not found_num:
                    randx = np.random.normal(mu, sigma)
                    max_rand = mu + (n - grade + self.min_grade) * sigma * 0.4
                    if randx < max_rand and (randx > distribution[n - 1] or n==0):
                        distribution[n] = np.clip(randx, 1, 99)
                        found_num = True

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
        similarity_last = abs(q_percent - self.last_percentage) * percentage_weight / float(100)
        similarity_percent = abs(q_percent - self.percentage) * percentage_weight * self.qs_answered / float(q_answers*100)
        difference_score = similarity_last + similarity_percent + difference_score

        # compare last question by token sort ratio
        similarity_q = fuzz.token_sort_ratio(row['question'], self.last_question) / float(100)
        question_weight = 1
        difference_score += question_weight * similarity_q

        # Compare test type
        similarity_test = fuzz.ratio(row['examName'], self.test_type) / float(100)
        test_weight = 1
        difference_score += similarity_test * test_weight

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

        self._update_by_index()

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

    def send_question(self):
        return self.last_question, self.A, self.B, self.C, self.D


# 5)) We create an API on which to get / send answers
# Get call to send a question
# Post call to get answer from user and update db
