import sys
import time
import random
import csv
import argparse
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QMainWindow
from PyQt5 import QtCore


__version__ = '0.1.1'

#GUI options
window_height = 0.20
window_width = 0.40
padding = 0.02

class QuestionWindow(QMainWindow):

    def __init__(self,app):

        super().__init__()
        self.app = app
        return

    #runs the question window,
    #Gets stuck in infinite loop until all question are answered
    def runWindow(self,questions):

        self.questions = questions
        self.current_question_index = 0
        self.setUI()
        self.newQuestion()
        self.window.show()
        self.app.exec_()

    #Clear up the UI and make a new question
    def newQuestion(self):

        if self.current_question_index >= len(self.questions):
            self.window.close()
            return

        self.current_question = self.questions[self.current_question_index]
        self.current_question_index += 1

        self.question_text.setText(self.current_question['question'])
        self.btn1.setText(self.current_question['choice_1'])
        self.btn2.setText(self.current_question['choice_2'])
        self.btn3.setText(self.current_question['choice_3'])
        self.btn1.setStyleSheet("background-color: none")
        self.btn2.setStyleSheet("background-color: none")
        self.btn3.setStyleSheet("background-color: none")

    #Gets called when a button is pressed
    def buttonClicked(self):

        if self.sender().text() == self.current_question['correct']:
            self.newQuestion()
        else:
            self.sender().setStyleSheet("background-color: red")
        return

    #Setup the UI
    def setUI(self):

        dimensions = self.getWindowDimensions()

        self.window = QWidget()
        self.window.setMaximumHeight(dimensions['window_height'])
        self.window.setMinimumHeight(dimensions['window_height'])
        self.window.setMaximumWidth(dimensions['window_width'])
        self.window.setMinimumWidth(dimensions['window_width'])
        self.window.setWindowModality(QtCore.Qt.WindowModal)
        self.window.setWindowFlags(
            QtCore.Qt.Widget|
            QtCore.Qt.CustomizeWindowHint|
            QtCore.Qt.FramelessWindowHint )
        self.window.move(dimensions['window_x'], dimensions['window_y'])

        self.question_text = QLabel(self.window)
        self.question_text.resize(dimensions['text_width'],dimensions['text_height'])
        self.question_text.move(dimensions['text_x'],dimensions['text_y'])

        self.btn1 = QPushButton(self.window)
        self.btn1.resize(dimensions['button_width'],dimensions['button_height'])
        self.btn1.move(dimensions['button_x1'], dimensions['button_y'])  
        self.btn1.clicked.connect(self.buttonClicked)

        self.btn2 = QPushButton(self.window)
        self.btn2.resize(dimensions['button_width'],dimensions['button_height'])
        self.btn2.move(dimensions['button_x2'], dimensions['button_y'])  
        self.btn2.clicked.connect(self.buttonClicked)

        self.btn3 = QPushButton(self.window)
        self.btn3.resize(dimensions['button_width'],dimensions['button_height'])
        self.btn3.move(dimensions['button_x3'], dimensions['button_y'])  
        self.btn3.clicked.connect(self.buttonClicked)
        return 

    def getWindowDimensions(self):

        dimensions = {}

        #Get screen dimensions
        screen = self.app.primaryScreen()
        dimensions['name'] = screen.name()
        dimensions['screen_width'] = screen.size().width()
        dimensions['screen_height'] = screen.size().height()
        dimensions['window_height'] = dimensions['screen_height'] * window_height
        dimensions['window_width'] = dimensions['screen_width'] * window_width
        dimensions['window_x'] = dimensions['screen_width'] / 2 - dimensions['window_width'] / 2
        dimensions['window_y'] = dimensions['screen_height'] / 2 - dimensions['window_height'] / 2

        #Calculate button dimensions
        but_padding = dimensions['window_height'] * padding
        dimensions['button_width'] = dimensions['window_width'] / 3 - but_padding
        dimensions['button_height'] = dimensions['window_height'] / 3 - but_padding
        dimensions['button_y'] = 2 * dimensions['window_height'] / 3 
        dimensions['button_x2'] = dimensions['window_width'] / 2 - dimensions['button_width'] / 2 
        dimensions['button_x1'] = 1 * dimensions['window_width'] / 6 - dimensions['button_width'] / 2 
        dimensions['button_x3'] = 5 * dimensions['window_width'] / 6 - dimensions['button_width'] / 2 

        #Calculate question text dimensions
        dimensions['text_width'] = dimensions['window_width'] * 0.9
        dimensions['text_height'] = dimensions['window_height'] * 0.2
        dimensions['text_x'] = dimensions['window_height'] * 0.1
        dimensions['text_y'] = dimensions['window_height'] * 0.1
        return dimensions

class QuestionMaker():

    def __init__(self):

        return

    #Makes the random list of question, incorrect options and answers
    def makeRandomList(self,questionNumber,questionFile):

        #Open the question file
        with open(questionFile,'r') as f:
            reader = csv.reader(f)
            self.questions = list(reader)

        questionList = []
        indexList = random.sample(range(0, len(self.questions)), len(self.questions))

        for i in indexList:

            choices = random.sample(range(1,4),3)

            tempList = indexList.copy()
            tempList.remove(i)
            incorrect_1 = tempList[random.randint(0,len(tempList)-1)]
            tempList.remove(incorrect_1)
            incorrect_2 = tempList[random.randint(0,len(tempList)-1)]

            current = {}
            current['question'] = self.questions[i][0]
            current['correct'] = self.questions[i][1]
            current['choice_{}'.format(choices[0])] = self.questions[i][1]
            current['choice_{}'.format(choices[1])] = self.questions[incorrect_1][1]
            current['choice_{}'.format(choices[2])] = self.questions[incorrect_2][1]
            questionList.append(current)

        questionList = self.padList(questionNumber,questionList)

        return questionList

    #Pads the question list so it is an multiple of the number of question per test
    def padList(self,questionNumber,questionList):

        if questionNumber < len(questionList):

            questionReps = int(len(questionList) / questionNumber)
            questionList = questionList[:(questionReps*questionNumber)]

        elif questionNumber > len(questionList):

            questionOverflow = questionNumber % len(questionList)
            questionList = questionList + questionList[0:questionOverflow]

        return questionList

#Make the command line arguments
def makeArgs():

    parser = argparse.ArgumentParser(description='vocabBuilder CLI V{}'.format(__version__),
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('wordList',
            metavar='WORDLIST',
            type=str,
            nargs=1,
            help='CSV file containing list of words and translations')
    parser.add_argument('-q','--questions',
            metavar='',
            type=int,
            nargs='?',
            default=5,
            help='Number of question in a test, defaults to 5')
    parser.add_argument('-t','--time',
            metavar='',
            type=int,
            nargs='?',
            default=10,
            help='Minutes between each test, defaults to 10 minutes')
    parser.add_argument('-v','--v',action='version',
            version='vocableBuilder CLI V{}'.format(__version__),help='Display program version')
    return parser


if __name__ == '__main__':

    parser = makeArgs()
    options = vars(parser.parse_args())

    if not os.path.exists(os.path.abspath(options['wordList'][0])):
            print('Error: File {} does not exist'.format(options['wordList'][0]))
            sys.exit()

    app = QApplication(sys.argv)
    window = QuestionWindow(app)
    questions = QuestionMaker()

    while True:

        questionList = questions.makeRandomList(options['questions'],options['wordList'][0])
        currentIndex = 0

        while currentIndex < len(questionList):

            window.runWindow(questionList[currentIndex:currentIndex+options['questions']])
            currentIndex += options['questions']
            time.sleep(options['time'] * 60)

