#! /usr/bin/python3


'''
Teacher Assistant\'s Assistant
'''

import pexpect
import pickle
import os, sys


BASE_PATH = '/home/skeledrew/Edu/LUC/Spring 2017/TA/COMP 170/'
ASS_TYPES = ['mpl', 'jfiles', 'quiz', 'jproj']
ASS_ACTIONS = ['View submission text', 'View submission attachments', 'View feedback attachments', 'View feedback text', 'View and edit comments', 'Grade assignment']
DOC_TYPES = ['doc', 'docx', 'pdf', 'odt', 'rtf', 'wps']
IMG_TYPES = ['png', 'bmp', 'gif', 'jpg', 'jpeg']
SRC_TYPES = ['java', 'c', 'cpp', 'cs', 'py']
ARC_TYPES = ['zip', 'tar', 'gz']
COMM_SEP = ' | '
TA_SIG = '- Andrew_'


def pickleLoad(fName):

    with open(fName, 'rb') as f:
        return pickle.load(f)

def pickleSave(obj, fName):

    with open(fName, 'wb') as f:
        pickle.dump(obj, f)
    return

def fileList(path, fullpath=False):
    nameList = os.listdir(path)

    if fullpath:

        for idx in range(len(nameList)):
            nameList[idx] = path + '/' + nameList[idx]
    return nameList

def loadText(path):
    text = ''

    with open(path) as f:

        for line in f:
            text += line
    return text

def saveText(text, path):

    with open(path, 'w') as f:

        if type(text) == type([]):

            for line in text:
                f.write(line + '\n')

        elif type(text) == type(''):
            f.write(text)

def getChoice(optsList, msg='', ret='string', pageSize=-1):

    if msg == '':
        msg = 'Choose an option:'
    print('\n' + msg)
    page = 1

    while True:

        for idx in range(len(optsList)):
            print(str(idx) + ': ' + optsList[idx])

        if pageSize > 0:
            pass

        try:
            choice = int(input('>> '))

            if choice in range(len(optsList)):
                return optsList[choice] if ret == 'string' else choice
            print('Invalid choice')

        except:
            print('Invalid input')


def prepAss(path):
    workDir = path + getChoice(['!quit!'] + fileList(path), msg='Select assignments folder:')
    if '!quit!' in workDir: return '', '', '!quit!'
    print('Assignments at ' + workDir)
    gradesPath = workDir + '/grades.csv'# + getChoice(fileList(workDir), 'Select grades file:')
    print('Grades file is ' + gradesPath)
    assType = getChoice(['!quit!', '!back!'] + ASS_TYPES)
    if not '!' in assType: print('Assignment type is ' + assType)
    return workDir, gradesPath, assType

def gradeAss(workDir, gradesPath, assType):
    grades = []
    studIDs = []
    studDirs = fileList(workDir)

    for studDir in studDirs:
        # ensure only student dirs are included

        if not ',' in studDir and not '(' in studDir and not studDir[-1] == ')':
            # simple check for a student directory
            studDirs.remove(studDir)

    with open(gradesPath) as fo:
        # load grades file; should prob just use loadText...

        for line in fo:
            grades.append(line.strip())  # remove newline
    studIDs.append('!quit!')

    for idx in range(len(grades)):
        # get the IDs

        if idx < 3:
            continue  # to the first student

        if grades[idx] == '':
            continue  # should actually break out, but...
        entry = grades[idx].split(',')

        if not len(entry) == 5:
            raise Exception('Error: Field size mismatch')
        lastGrade = ' [--]' if entry[-1] == '""' else ' [' + entry[-1][1:-1] + ']'
        studIDs.append(entry[1][1:-1] + lastGrade)  # grab the id and grade info
    maxGrade = int(input('Enter the maximum grade students can get for %s: ' % workDir.split('/')[-1]))

    while True:
        # work on assignments
        student = getChoice(studIDs, msg='Select student to work with:')
        if ' ' in student: student = student.split(' ')[0]

        if student == '!quit!':
            print('Exiting grading session')
            break

        for studDir in studDirs:
            # search students

            if '(' + student + ')' in studDir:
                # find the correct student directory via ID
                # NB: all parts of the assignment must be batch downloaded!
                studDirPath = workDir + '/' + studDir + '/'
                subText = loadText(studDirPath + studDir + '_submissionText.html')
                subAtts = fileList(studDirPath + 'Submission attachment(s)', fullpath=True)
                feedText = loadText(studDirPath + 'feedbackText.html')
                feedAtts = fileList(studDirPath + 'Feedback Attachment(s)', fullpath=True)
                commFile = studDirPath + 'comments.txt'

                while True:
                    msg = 'Select an action to perform on %s\'s assignment' % student
                    act = getChoice(['!quit!'] + ASS_ACTIONS, msg=msg)

                    if act == '!quit!':
                        print('Exiting %s\'s assignment view' % student)
                        break

                    if act == ASS_ACTIONS[0]:
                        viewText(subText)
                        continue

                    if act == ASS_ACTIONS[3]:
                        viewText(feedText)
                        continue

                    if act == ASS_ACTIONS[1]:
                        viewAtts(subAtts)
                        continue

                    if act == ASS_ACTIONS[2]:
                        viewAtts(feedAtts)
                        continue

                    if act == ASS_ACTIONS[4]:
                        editComm(commFile)
                        continue

                    if act == ASS_ACTIONS[5]:
                        # calculate grade from comments and record
                        studGrade = maxGrade
                        comments = loadText(commFile)

                        for comm in comments.split(COMM_SEP):
                            # tally grade points

                            '''if comm[-1] in [str(i) for i in range(10)] and int(comm.split(' ')[-1]) == 0:
                                # overall grade is 0
                                studGrade = 0
                                break'''

                            if comm[-1] in [str(i) for i in range(10)]:
                                # comment includes grade affecting info
                                modifier = int(comm.split(' ')[-1])

                                if modifier == 0:
                                    studGrade = 0
                                    break
                                studGrade += int(comm.split(' ')[-1])

                        for idx in range(len(grades)):
                            # record grade

                            if '"' + student + '"' in grades[idx]:
                                lastGrade = grades[idx].split(',')[-1][1:-1]
                                print('Changed %s\'s grade from %s to %s' % (student, lastGrade, str(studGrade)))
                                studGrade = '"' + str(studGrade) + '"'
                                grades[idx] = ','.join(grades[idx].split(',')[:-1] + [studGrade])
                                saveText(grades, gradesPath)

                        for idx in range(len(studIDs)):
                            # update student menu printable with new grade

                            if student in studIDs[idx]:
                                studIDs[idx] = studIDs[idx].split(' ')[0] + ' [' + studGrade[1:-1] + ']'

                    if assType == 'mpl':
                        grade = gradeMPL(act, subText, subAtts, feedText, feedAtts, comments)

                    if assType == 'jfiles':
                        grade = gradeJFiles(act, subText, subAtts, feedText, feedAtts, comments)

                    if assType == 'quiz':
                        grade = gradeQuiz(act, subText, subAtts, feedText, feedAtts, comments)

                    if assType == 'jproj':
                        grade = gradeJProject(act, subText, subAtts, feedText, feedAtts, comments)

def gradeMPL(act, sT, sA, fT, fA, com):

    if act == ASS_ACTIONS:
        pass

def gradeJFiles(act, sT, sA, fT, fA, com):
    pass

def gradeQuiz(act, sT, sA, fT, fA, com):
    pass

def gradeJProject(act, sT, sA, fT, fA, com):
    pass

def viewText(text):
    # should choose in line or web browser based on length
    print('File text: ' + text)

def viewAtts(attDir):

    while True:
        choice = getChoice(['!quit!'] + [att.split('/')[-1] for att in attDir], msg='Select file to view:')
        if choice == '!quit!': break
        fullPath = '/'.join(attDir[0].split('/')[:-1]) + '/' + choice
        ext = choice.split('.')[-1]

        if ext in IMG_TYPES:
            # invoke image viewer
            pass

        elif ext in DOC_TYPES:
            # invoke doc viewer

            if ext == 'doc' or ext == 'docx' or ext == 'rtf':
                print('Opening %s in WPS Office' % choice)
                child = pexpect.spawn('wps "%s"' % fullPath)
                child.expect('')
                continue

            if ext == 'pdf':
                print('Opening %s in Okular' % choice)
                child = pexpect.spawn('okular "%s"' % fullPath)
                child.expect('')
                continue

            print('No associated handler for ' + choice)

        elif ext in SRC_TYPES:
            # invoke editor

            if ext == 'java':
                results = handleJava(fullPath, commFile='/'.join(attDir[0].split('/')[:-2]) + '/comments.txt')
                continue

        else:
            # prompt for viewer
            pass

def handleJava(path, commFile):
    results = {}
    fName = path.split('/')[-1]
    options = ['!quit!', 'Compile %s' % fName, 'View %s inline' % fName, 'View %s in Kate' % fName]
    options += ['Run %s' % fName.split('.')[0] + '.class', 'Analyze %s' % fName, 'Edit comments']

    while True:
        act = getChoice(options)

        if act == '!quit!':
            print('Leaving Java management.')
            break

        if act == options[1]:
            # Attempt compile
            child = pexpect.spawn('javac "%s"' % path)
            idx = child.expect(['error', pexpect.EOF])

            if idx == 0:
                results['compiled'] = False
                print('Error: Failed to compile %s' % fName)

            else:
                results['compiled'] = True
                print('Compile successful!')

        if act == options[2]:
            print('\n\n%s\n\n' % loadText(path))
            input('Press any key to continue')

        if act == options[3]:
            print('Opening %s in Kate' % fName)
            pexpect.run('kate "%s"' % path)

        if act == options[4]:
            # Run the class file
            classFile = fName.split('.')[0]
            mode = getChoice(['interactive', 'dumb'], msg='Select a mode to run %s' % classFile)
            print('Running %s in %s mode' % (classFile, mode))

            if mode == 'dumb':
                # no input expected
                child = pexpect.spawnu('java -cp "%s" %s' % ('/'.join(path.split('/')[:-1]), fName.split('.')[0]), timeout=5)
                child.logfile_send = open('temp.out', 'wb')
                child.expect([pexpect.TIMEOUT, pexpect.EOF])
                child.logfile_send.close()
                child.logfile_send = None
                print(loadText('temp.out'))

            else:
                # interact with user
                child = pexpect.spawnu('java -cp "%s" %s' % ('/'.join(path.split('/')[:-1]), fName.split('.')[0]))

                try:
                    child.interact()

                except Exception as e:
                    print('Interaction with %s failed. Maybe it exited?' % fName.split('.')[0])
                    print('Error detail: ' + str(e))
            #child.logfile.close()

            '''while True:
                child.logfile_send = open('temp.out', 'wb')
                child.logfile_read = sys.stdout
                idx = child.expect(['', pexpect.EOF, pexpect.TIMEOUT])
                print(loadText('temp.out'))
                child.send(input())
                print('Expect got %d' % idx)
                child.logfile_send.close()  # close so content is purged

                if idx > 0:
                    break'''
            continue

        if act == options[5]:
            print('Not yet implemented!')
            continue

        if act == options[6]:
            editComm(commFile, ASS_TYPES[1], fName)
            continue
    return results

def handleArchive(path):
    ## actions are list and extract
    pass

def editComm(commFile, assType='', fName=''):
    globalComments = loadText(BASE_PATH + 'Comments.txt').split('\n')
    comments = loadText(commFile)
    localComments = []

    if COMM_SEP in comments:
        # prepare existing comments for editing
        comments = comments.strip().split(COMM_SEP)

        for comm in comments:
            # remove existing non-comments for easier manipulation

            if not comm[-1] in [str(i) for i in range(10)] and not comm in globalComments:
                # leave grade-affecting comments intact even if removed from master file
                comments.remove(comm)

    elif '\n' in comments:
        # manually created
        comments = comments.split('\n')

    elif len(comments) > 5:
        # single line of comments, prob done in Sakai
        print('Unable to handle single line comments yet')
        pass

    else:
        # nothing there that matters
        comments = []

    while True:
        localComments = ['!quit!', '!add new comment!', '!view current comments!']

        for comm in globalComments:
            # create format to add and remove comments

            if comm == '':
                # zap empty lines; TODO: figure out what's causing them
                continue

            if comm in comments or (assType == ASS_TYPES[1] and '%s: %s' % (fName, comm) in comments):
                localComments.append('[del] ' + comm)

            else:
                localComments.append('[add] ' + comm)
        act = getChoice(localComments)

        if act == localComments[0]:
            print('Leaving comments editor')
            saveText(globalComments, BASE_PATH + 'Comments.txt')
            break

        elif '[del] ' in act:
            print('Removed comment: ' + act[6:])
            comments.remove(act[6:])

        elif '[add] ' in act:
            print('Added comment: ' + act[6:])
            comments.append(act[6:])

        elif act == localComments[1]:
            # add new comment
            newComment = input('Enter new comment: ').strip()

            if assType == ASS_TYPES[1] and not fName == '':
                # prepend the file name
                newComment = '%s: %s' % (fName, newComment)
            globalComments.append(newComment)
            comments.append(newComment)

        elif act == localComments[2]:
            print('\n\n%s\n\n' % '\n'.join(comments))
            input('Press any key to continue')

    if not comments == []:
        comments.append(TA_SIG)
    saveText(COMM_SEP.join(comments), commFile)
    return COMM_SEP.join(comments)

def main():

    while True:
        workDir, gradesPath, assType = prepAss(BASE_PATH)
        if assType == '!back!': continue
        if assType == '!quit!': break
        gradeAss(workDir, gradesPath, assType)
    print('Program terminated')

if __name__ == '__main__':
    main()
