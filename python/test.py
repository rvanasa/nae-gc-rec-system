import os

"""
TODO:
    Create New USER sqlite integration, Add Password option?
    Connect to flask fully, test API alone
    Connect to frontends
    Look through some of the weirder errors (negative percentage corrects?)
"""

from recs import Recsystem

BASE = os.path.abspath('..') + '/data/Qs'
grade = 4
test = 'MCAS'

rc = Recsystem(BASE, 'ttrojan77')

q, a, b, c, d = rc.send_question()
last_percent = rc.send_q_stats()
print(str(last_percent) + " of students in your grade got this question right")
print(q)
print(a)
print(b)
print(c)
print(d)
print(" ")

ANSWER = 'D'

rc.prep_next_q(ANSWER)

q, a, b, c, d = rc.send_question()
last_percent = rc.send_q_stats()
print(str(last_percent) + " of students in your grade got this question right")
print(q)
print(a)
print(b)
print(c)
print(d)
