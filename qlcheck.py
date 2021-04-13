import csv
import argparse
from os.path import isfile
from sys import exit
from dataclasses import dataclass

@dataclass
class Student:
    firstName: str
    lastName: str
    email: str

@dataclass
class Lab:
    labName: str
    toCheck: bool

@dataclass
class Attempt:
    creditsUsed: int
    usedOn: str
    user: str
    email: str
    labName: str
    runtime: int
    duration: int
    percentComplete: int

@dataclass
class StudentAttempt:
    student: Student
    lab: Lab
    attempt: Attempt
    
parser = argparse.ArgumentParser(description='Easily determine Qwiklabs completions for your students')
parser.add_argument('--students', help='A CSV file containing a list of students', required=True)
parser.add_argument('--report', help='A CSV file containing the Qwiklabs completion report', required=True)
parser.add_argument('--lab', help='Check completion for a specific named lab', required=False)
parser.add_argument('--labs', help='A CSV file containing a list of Qwiklabs', required=True)
parser.add_argument('--noHeaders', help='Indicate CSV files contain no header row', default=False)
parser.add_argument('--justIncomplete', help='Just show lab results for incomplete labs', action='store_true')
parser.add_argument('--completeThreshold', help='Set the threshold for an assignment to be considered complete', default=100)
args = parser.parse_args()
print(args)

if not isfile(args.students):
    print(f'Student file {args.students} does not exist')
    exit(-1)

if not isfile(args.report):
    print(f'Report file {args.report} does not exist')
    exit(-1)

if not isfile(args.labs):
    print(f'Labs file {args.labs} does not exist')
    exit(-1)

# Process the student file, creating the needed student records
students = { }
with open(args.students) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if not args.noHeaders and line_count == 0:
            # Skip the header line
            line_count += 1
        else:
            line_count += 1
            students[row[2].strip()] = Student(lastName = row[0].strip(), firstName = row[1].strip(), email = row[2].strip())
    print(f'Loaded {len(students)} students')

# Process the labs file, create the needed lab records
labs = { }
with open(args.labs) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if not args.noHeaders and line_count == 0:
            # Skip the header line
            line_count += 1
        else:
            line_count += 1
            labs[row[0].strip()] = Lab(labName = row[0].strip(),toCheck=(row[1].strip() == 'Y' or row[1].strip() == 'y'))
    print(f'Loaded {len(labs)} labs')

# Process the attempts file, create the needed attempt records
attempts = [ ]
with open (args.report) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if not args.noHeaders and (line_count == 0 or line_count == 1):
            # Skip the header lines (there are two)
            line_count += 1
        else:
            line_count += 1
            attempt = Attempt(creditsUsed=row[0].strip(), usedOn=row[1].strip(), user=row[2].strip(), email=row[3].strip(), labName=row[4].strip(), runtime=row[5].strip(), duration=row[6].strip(), percentComplete=row[7].strip())
            if (attempt.email in students and attempt.labName in labs and labs[attempt.labName].toCheck):
                attempts.append(attempt)
    print(f'Loaded {len(attempts)} attempts')

# Use loaded information to link up students, labs, and attempts
studentAttempts = [ ]
for attempt in attempts:
    studentAttempts.append(StudentAttempt(student=students[attempt.email], lab=labs[attempt.labName], attempt=attempt))
print(f'Created {len(studentAttempts)} records')

# Using completion information, by lab, track the highest percent each student has scored in each lab
completionsByLab = { }
for labName in sorted(labs):
    completionsByLab[labName] = { }

for labName in sorted(labs):
    for studentEmail in sorted(students):
        completionsByLab[labName][studentEmail] = 0

for attempt in studentAttempts:
    if int(attempt.attempt.percentComplete) > int(completionsByLab[attempt.lab.labName][attempt.student.email]):
        completionsByLab[attempt.lab.labName][attempt.student.email] = attempt.attempt.percentComplete

# Print the results
print('')
for labName in sorted(labs):
    if labs[labName].toCheck:
        print(labName)
        for studentEmail in sorted(students):
            if args.justIncomplete:
                if int(completionsByLab[labName][studentEmail]) < args.completeThreshold:
                    print(f'{studentEmail}: {completionsByLab[labName][studentEmail]}')
            else:
                print(f'{studentEmail}: {completionsByLab[labName][studentEmail]}')
        print('')
