import os

from recs import Recsystem

BASE = os.path.abspath('..') + '/data/Qs'
grade = 4
test = 'MCAS'

rc = Recsystem(BASE, grade, test)



