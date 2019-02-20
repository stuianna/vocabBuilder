import sys
import time
import random
import csv
import argparse
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QMainWindow, QHBoxLayout, QGroupBox, QVBoxLayout, QGridLayout, QSpinBox, QFileDialog, QMessageBox, QSystemTrayIcon, QMenu, QAction, QStyle, QSpacerItem, QSizePolicy
from PyQt5 import QtCore, QtGui, QtTest
from PyQt5.QtGui import QIcon, QPixmap

#This needs to be included so the app knowns the correct path to loo
#for resource files
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the pyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    dir_path = sys._MEIPASS + os.sep
else:
    dir_path = os.path.dirname(os.path.abspath(__file__)) + os.sep

__version__ = '0.2.0'

#GUI testing screen options
window_height = 0.20
window_width = 0.40
padding = 0.02

#Program type CLI/GUI
mode = 'CLI'

#Testing variable for pause/run
testing = True

class MainMenu(QMainWindow):

    def __init__(self,app):

        super().__init__()
        self.app = app
        self.exitStatus = None
        return

    def runWindow(self):

        self.loadSettings()
        self.setUI()
        self.window.show()
        self.app.exec_()

        if self.exitStatus == 'start':
            self.saveSettings()

        return self.exitStatus,         \
            self.fileName,              \
            self.spin_time.value(),     \
            self.spin_questions.value()

    def loadSettings(self):

        settings = QtCore.QSettings('vocabBuilder', 'config')

        self.time = settings.value('time', type=int)
        self.questions = settings.value('questions', type=int)
        self.fileName = settings.value('fileName', type=str)

        #If the filename is blank, then the settings file doesn't exist
        #and this is the first time the program has been run. Use default values.
        if self.fileName == '':
            self.time = 10
            self.questions = 5

    def saveSettings(self):

        settings = QtCore.QSettings('vocabBuilder', 'config')
        settings.setValue('time',self.spin_time.value())
        settings.setValue('questions',self.spin_questions.value())
        settings.setValue('fileName',self.fileName)
        return

    def setUI(self):

        self.window = QWidget()
        self.window.setWindowIcon(QtGui.QIcon(dir_path + 'resources/bbp.png'))
        self.window.setWindowTitle('vocabBuilder')


        self.btn_exit = QPushButton('Exit')
        self.btn_exit.clicked.connect(self.exitClicked)

        self.btn_start = QPushButton('Start')
        self.btn_start.clicked.connect(self.startClicked)

        # The start button should be initially disabled if no file exists
        if self.fileName == '':
            self.btn_start.setEnabled(False)

        # Check the file still exists and is valid
        else:
            self.btn_start.setEnabled(self.checkFileContents(self.fileName))

        self.btn_words = QPushButton('Words')
        self.btn_words.clicked.connect(self.wordsClicked)

        self.spin_time = QSpinBox()
        self.spin_time.setMinimum(1)
        self.spin_time.setValue(self.time)

        self.spin_questions = QSpinBox()
        self.spin_questions.setMinimum(1)
        self.spin_questions.setValue(self.questions)

        wordsLabel = QLabel('Questions:')
        timeLabel = QLabel('Time:')

        picLabel = QLabel()
        pixmap = QPixmap(dir_path + 'resources/bbp.png')
        picLabel.setPixmap(pixmap)

        mainLayout = QVBoxLayout(self.window)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(picLabel)

        vSpacer = QSpacerItem(5,10,
                QSizePolicy.Minimum, QSizePolicy.Expanding)

        hSpacer = QSpacerItem(10,5,
                QSizePolicy.Minimum, QSizePolicy.Expanding)

        rightLayout = QVBoxLayout()
        rightLayout.setSpacing(0)
        rightLayout.setContentsMargins(0,0,0,0)
        rightLayout.addWidget(timeLabel)
        rightLayout.addWidget(self.spin_time)
        rightLayout.addWidget(wordsLabel)
        rightLayout.addWidget(self.spin_questions)
        rightLayout.addItem(vSpacer)


        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(self.btn_words)
        bottomLayout.addWidget(self.btn_start)
        bottomLayout.addWidget(self.btn_exit)

        topLayout = QHBoxLayout()
        topLayout.addLayout(leftLayout)
        topLayout.addLayout(rightLayout)

        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(bottomLayout)

        self.window.setFixedSize(mainLayout.sizeHint())
        return 

    def exitClicked(self):

        self.exitStatus = 'exit'
        self.window.close()
        return 

    def startClicked(self):

        self.exitStatus = 'start'
        self.window.close()
        return 

    def wordsClicked(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,
                "Open word dictionary file", 
                self.fileName,
                "CSV Files (*.csv)", 
                options=options)

        fileName = os.path.abspath(fileName)

        if fileName:

            if not self.checkFileContents(fileName):
                self.btn_start.setEnabled(False)
                return
        else:
            print('No file selected')
            return

        #If we get this far then the file seems ok.
        self.fileName = fileName
        self.btn_start.setEnabled(True)
        return 

    def checkFileContents(self,fileName):

        try:
            with open(fileName,'r',encoding="utf8") as f:
                reader = csv.reader(f)
                questions = list(reader)
        except:
            print('Cannot open selected file')
            return False

        #Check there is enougth words
        if len(questions) < 1:
                QMessageBox.warning(self.window,'Open File Warning',
                        'Problem with language file, not enougth words.')
                return False

        #Check there is enougth translations
        languageNumber = len(questions[0])

        if languageNumber < 2:
            QMessageBox.warning(self.window,'Open File Warning',
                    'Problem with language file, not enougth translations.')
            return False

        #Check that each listing has the same number of translations
        for question in questions:

            if len(question) != languageNumber:
                QMessageBox.warning(self.window,'Open File Warning',
                        'Number of translations does not match.\n{}'.format(question))
                return False

        return True

class TrayIcon(QMainWindow):

    def __init__(self,app):

        super().__init__()
        self.app = app
        return

    def runTray(self):

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(dir_path + 'resources/bbp.png'))

        quit_action = QAction("Exit", self)
        self.pause_action = QAction("Pause", self)
        quit_action.triggered.connect(sys.exit)
        self.pause_action.triggered.connect(self.pause)
        tray_menu = QMenu()
        tray_menu.addAction(self.pause_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def pause(self):

        global testing

        if testing == True:
            testing = False
            self.pause_action.setText('Resume')
        else:
            testing = True
            self.pause_action.setText('Pause')

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
        return

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
        self.window.setWindowIcon(QtGui.QIcon(dir_path + 'resources/bbp.png'))
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
        with open(questionFile,'r',encoding="utf8") as f:
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
            version='vocabBuilder CLI V{}'.format(__version__),help='Display program version')
    return parser

def runCLI():

    parser = makeArgs()
    options = vars(parser.parse_args())

    #Check the passed file exists before continuing
    if not os.path.exists(os.path.abspath(options['wordList'][0])):
            print('Error: File {} does not exist'.format(options['wordList'][0]))
            sys.exit()

    options['wordList'] = options['wordList'][0]

    return options

def runGUI():

    options = {}

    status, options['wordList'], options['time'], options['questions'] = menu.runWindow()

    if status == 'exit':
        sys.exit()

    elif status == 'start':
        pass
    else:
        sys.exit()

    return options


if __name__ == '__main__':

    app = QApplication(sys.argv)
    menu = MainMenu(app)
    window = QuestionWindow(app)
    questions = QuestionMaker()

    if mode == 'GUI':

        tray = TrayIcon(app)
        tray.runTray()
        options = runGUI()

    elif mode == 'CLI':

        options = runCLI()
        tray = TrayIcon(app)
        tray.runTray()

    else:
        print('Unknown mode type, options are GUI or CLI')
        sys.exit()

    #Testing loop, gets stuck here until exited using the tray icon options
    while True:

        questionList = questions.makeRandomList(options['questions'],options['wordList'])
        currentIndex = 0

        while currentIndex < len(questionList):

            if testing is True:
                window.runWindow(questionList[currentIndex:currentIndex+options['questions']])
                currentIndex += options['questions']

            #Need to use QT sleep function so the UI and Tray icon is active
            QtTest.QTest.qWait(options['time'] * 60 * 1000)

