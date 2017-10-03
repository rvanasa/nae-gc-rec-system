AI2 Science Questions v2 (May 2017)

*****
These science exam questions guide our research into multiple science exam question answering at the elementary and middle school science levels. This download contains elementary level and middle school level questions in multiple choice format, both with and without associated diagrams. The questions come pre-split into Train, Development, and Test sets. 

All questions are provided in CSV format containing the full text of the question, any applicable image reference(s), and its answer options in one cell. The accompanying images are provided in a separate directory.
All questions are additionally provided in JSONL format, containing a split version of the question where the question text has been separated from the answer options programatically.

Please contact ai2-data@allenai.org with any questions regarding this data set.

*****

Comma-delimited (CSV) columns:
   questionID - a unique identifier for the question (our own numbering)
   originalQuestionID - the question number on the test
   totalPossiblePoint - how many points the question is worth when scoring
   AnswerKey - the correct answer option
   isMultipleChoiceQuestion - 1 = multiple choice, 0 = other
   includesDiagram - 1 = includes diagram, 0 = other
   examName - the source of the exam
   schoolGrade - grade level
   year - publication year of the exam
   question - the text of the question itself
   subject - the general question topic
   category - Test, Train, or Dev

*****

The JSONL files contain the same questions split into the “stem” of the question (the question text) and then the various answer “choices” and their corresponding labels (A, B, C, D). The questionID is also included. When an image is present, its file reference is inserted.

*****

The questions in the dataset have been extracted from the following state and regional sources:

* AIMS-Arizona's Instrument to Measure Standards
* Alaska Department of Education & Early Development
* Arkansas Department of Education
* California Standards Test
* Louisiana Department of Education
* Massachusetts Department of Education
* MCAS-Massachusetts Comprehensive Assessment System
* Maryland School Assessment
* MEA-Maine Educational Assessment
* MEAP-Michigan Educational Assessment Program
* NAEP-National Assessment of Educational Progress
* North Carolina End-of-Grade Assessment
* New York State Educational Department Regents exams
* Ohio Achievement Tests
* TAKS-Texas Assessment of Knowledge and Skills
* TIMSS 1995, 2003, 2007, & 2011 Assessments. Copyright © 2013 International Association for the Evaluation of Educational Achievement (IEA)
* Virginia Standards of Learning
* Washington MSP

***** 

Release notes:

AI2 Science Questions v2 expands the size of our openly available multiple choice science question set to 5,060 questions via the inclusion of many newly sourced, genuine exam questions from a variety of state assessments. This set also removes some erroneous questions and duplicate questions detected in v1 of the set.