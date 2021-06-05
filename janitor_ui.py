import sys
import random
from collections import OrderedDict
# from functools import partial

from PySide import QtGui
from PySide import QtCore

import janitor_cmds as janitorCmds
import coreUtils

class Colors():
    # red           = QtGui.QColor(120, 000, 000)
    # green         = QtGui.QColor(000, 120, 000)
    # blue          = QtGui.QColor(100, 100, 220)
    # orange        = QtGui.QColor(200, 100, 000)
    # yellow        = QtGui.QColor(255, 255, 000)

    red_dim       = QtGui.QColor(90.0, 025.0, 025.0)

    green_dim     = QtGui.QColor(85.0, 107.0, 47.0)
    # orange_dim    = QtGui.QColor(100, 050,  50)
    orange_dim    = QtGui.QColor(255.0, 102.0,   0.0)
    blue_dim      = QtGui.QColor(50.0,   50.0, 110.0)
    yellow_dim    = QtGui.QColor(180.0, 180.0,   0.0)

    lightGrey     = QtGui.QColor(120.0, 120.0, 120.0)
    grey          = QtGui.QColor(100.0, 100.0, 100.0)
    darkGrey      = QtGui.QColor(050.0, 050.0, 050.0)
    darkerGrey    = QtGui.QColor(040.0, 040.0, 040.0)
    black         = QtGui.QColor(000.0, 000.0, 000.0)


def randomColor(alpha=255):

    return QtGui.QColor(random.randint(0,255), random.randint(0,255), random.randint(0,255), alpha)


def setBgCol(widget, color):
    palette = widget.palette()
    palette.setColor(widget.backgroundRole(), color)
    widget.setAutoFillBackground(True)

    widget.setPalette(palette)


class LayoutWidget(QtGui.QWidget):
    def __init__(self, mode='vertical', parent=None):
        super(LayoutWidget, self).__init__(parent=parent)
        if mode in ('vertical', 'horizontal'):
            self.layout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight, parent=self)  # On est oblige de donner une direction a la creation du layout
            if mode == 'horizontal':
                self.layout.setDirection(QtGui.QBoxLayout.LeftToRight)
            elif mode =='vertical':
                self.layout.setDirection(QtGui.QBoxLayout.TopToBottom)
        elif mode == 'grid':
            self.layout = QtGui.QGridLayout(self)  # On est oblige de donner une direction a la creation du layout
        else:
            raise()

        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def addWidget(self, *args, **kwargs):
        self.layout.addWidget(*args, **kwargs)

    def setMargins(self, left=0, top=0, right=0, bottom=0):
        self.layout.setContentsMargins(left, top, right, bottom)



class TaskWidget(QtGui.QFrame):
    activeStateChanged = QtCore.Signal()

    styleSheet = ''\
    'QFrame{'\
    '    border-radius: 8px;'\
    '    padding: 2px;'\
    '    background-color: rgb(200, 60, 102);'\
    '}'
    # '    border: 2px solid green;'\

    def __init__(self, task, parent=None):
        super(TaskWidget, self).__init__(parent=parent)
        self.task         = task
        self.neutralColor = Colors.lightGrey
        self.okColor      = Colors.green_dim
        self.pbColor      = Colors.orange_dim

        self.checkBox    = QtGui.QCheckBox()
        self.checkButton = QtGui.QPushButton(task.niceName or '')
        self.fixButton   = QtGui.QPushButton('fix')
        self.noFixSpace  = QtGui.QWidget()
        self.helpButton  = QtGui.QPushButton('?')
        # self.descriptionLabel = QtGui.QLabel(self.task.description)
        self.descriptionLabel = QtGui.QTextEdit(self.task.description)
        # self.descriptionLabel.setWordWrap(True)
        self.descriptionLabel.setVisible(False)
        self.descriptionLabel.setReadOnly(True)


        if task.active:
            self.checkBox.setCheckState(QtCore.Qt.Checked)
        else:
            self.checkBox.setCheckState(QtCore.Qt.Unchecked)

        if self.task.fix is None:
            self.fixButton.setVisible(False)
            self.noFixSpace.setVisible(True)
        else:
            self.fixButton.setVisible(True)
            self.noFixSpace.setVisible(False)

        self.buttonsLayout = LayoutWidget(mode='horizontal', parent=self)
        self.buttonsLayout.setMargins(0, 0, 0, 0)

        self.buttonsLayout.addWidget(self.checkBox)
        self.buttonsLayout.addWidget(self.checkButton)
        self.buttonsLayout.addWidget(self.fixButton)
        self.buttonsLayout.addWidget(self.noFixSpace)
        self.buttonsLayout.addWidget(self.helpButton)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.buttonsLayout)
        self.layout.addWidget(self.descriptionLabel)
        self.setLayout(self.layout)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.checkBox.setFixedWidth(15)
        self.fixButton.setFixedWidth(25)
        self.noFixSpace.setFixedWidth(25)
        self.helpButton.setFixedWidth(25)
        self.helpButton.setFixedHeight(25)

        self.checkButton.clicked.connect(self.taskCheck)
        self.fixButton.clicked.connect(self.taskFix)
        self.checkBox.stateChanged.connect(self.setTaskActive)
        self.helpButton.clicked.connect(self.showHideDescription)

        self.resetColor()
        # self.setStyleSheet(self.styleSheet)

    def resetColor(self):
        setBgCol(self.checkButton, self.neutralColor)

    def updateColor(self):
        if self.task.toFix:
            setBgCol(self.checkButton, self.pbColor)
        else:
            setBgCol(self.checkButton, self.okColor)

    def showHideDescription(self):
        onOff = self.descriptionLabel.isVisible()
        self.descriptionLabel.setVisible(not onOff)

    def taskCheck(self):
        self.task.check()
        self.updateColor()

    def taskFix(self):
        if self.task.fix is not None:
            self.task.fix()
        self.taskCheck()

    def setTaskActive(self, state):
        if state > 0:
            self.task.active = True
        else:
            self.task.active = False
        self.activeStateChanged.emit()



class JanitorPanel(QtGui.QWidget):
    def __init__(self, janitor, parent=None):
        super(JanitorPanel, self).__init__(parent=parent)
        self.janitor      = janitor
        self.tasksWidgets = []


        self.layout = QtGui.QVBoxLayout(self)
        headerWLayout = LayoutWidget(mode='horizontal', parent=self)
        panelWLayout  = LayoutWidget(mode='vertical', parent=self)

        headerWLayout.setContentsMargins(5, 5, 5, 5)
        panelWLayout.setContentsMargins(5, 5, 5, 5)
        setBgCol(headerWLayout, randomColor())
        setBgCol(panelWLayout, randomColor())

        self.mainCheckBox     = QtGui.QCheckBox()
        self.mainLaunchButton = QtGui.QPushButton('GO')
        self.mainFixButton    = QtGui.QPushButton('fix')
        self.mainCheckFixCheckButton = QtGui.QPushButton('cfc')

        self.mainCheckBox.setFixedWidth(15)
        self.mainFixButton.setFixedWidth(25)
        self.mainCheckFixCheckButton.setFixedWidth(25)



        headerWLayout.addWidget(self.mainCheckBox)
        headerWLayout.addWidget(self.mainLaunchButton)
        headerWLayout.addWidget(self.mainFixButton)
        headerWLayout.addWidget(self.mainCheckFixCheckButton)

        # headerWLayout.layout.addSpacing(30)  # to help padding remaining space

        self.layout.addWidget(headerWLayout)
        self.layout.addSpacing(10)
        self.layout.addWidget(panelWLayout)

        for task in janitor.tasks:
            taskWidget = TaskWidget(task)
            self.tasksWidgets.append(taskWidget)
            panelWLayout.addWidget(taskWidget)

            taskWidget.activeStateChanged.connect(self.updateMainCheckBoxState)

        self.layout.addStretch()


        self.updateMainCheckBoxState()

        self.mainCheckBox.stateChanged.connect(self.changeAllTasksActiveStatus)
        self.mainLaunchButton.clicked.connect(self.mainLaunch)
        self.mainFixButton.clicked.connect(self.mainFix)
        self.mainCheckFixCheckButton.clicked.connect(self.mainCheckFixCheck)


    def updateTasksColors(self):
        for taskWidget in self.tasksWidgets:
            if taskWidget.task.active:
                taskWidget.updateColor()


    def mainLaunch(self):
        self.debug()
        self.janitor.check()
        self.updateTasksColors()

    def mainFix(self):
        self.debug()
        self.janitor.checkFixCheck(skipInactives=True)
        self.updateTasksColors()

    def mainCheckFixCheck(self):
        self.debug()
        errors = self.janitor.checkFixCheck(skipInactives=False)
        print 'errors =', errors
        self.updateTasksColors()

    def debug(self):
        tasks = [taskWidget.task for taskWidget in self.tasksWidgets]
        states = OrderedDict([(task.niceName,task.active) for task in tasks])
        print
        print ('states =', states)
        print (coreUtils.buildSmartPrintStr(states))


    def updateMainCheckBoxState(self):
        self.mainCheckBox.blockSignals(True)
        tasksStates = [task.active for task in self.janitor.tasks]
        if all(tasksStates):
            print ('all tasks are active')
            self.mainCheckBox.setCheckState(QtCore.Qt.Checked)
            self.mainCheckBox.setTristate(False)
        elif any(tasksStates):
            print ('some tasks are active')
            self.mainCheckBox.setCheckState(QtCore.Qt.PartiallyChecked)
            self.mainCheckBox.setTristate(True)
        else:
            print ('no tasks are active')
            self.mainCheckBox.setCheckState(QtCore.Qt.Unchecked)
            self.mainCheckBox.setTristate(False)

        print ('isTriState:',  self.mainCheckBox.isTristate())
        self.mainCheckBox.blockSignals(False)

    def changeAllTasksActiveStatus(self, arg):
        print ('arg =', arg)
        print ('isTriState:',  self.mainCheckBox.isTristate())

        checkState = QtCore.Qt.Checked if arg > 0 else QtCore.Qt.Unchecked
        for taskWidget in self.tasksWidgets:
            taskWidget.blockSignals(True)
            print ('taskWidget =', taskWidget)
            taskWidget.checkBox.setCheckState(checkState)
            taskWidget.blockSignals(False)
        self.mainCheckBox.setTristate(False)




class JanitorUi(QtGui.QWidget):
    """docstring for JanitorUi"""

    def __init__(self, parent=None):
        super(JanitorUi, self).__init__(parent=parent)

        self.janitors       = None
        self.allTaskWidgets = []
        self.janitorsPanels = None

        self.fakeScene = FakeScene()  # Une fake scene pour faire des pseudo checks/fix


        # top part with combobox and checkBox and go button
        self.janitorsCombox    = QtGui.QComboBox(parent=self)
        self.resetFakeSceneBtn = QtGui.QPushButton('ResetFakeScene')


        # Bottom part where all task button will go
        self.panelsWLayout   = LayoutWidget(mode='vertical', parent=self)


        # main layout
        self.mainLayout = QtGui.QVBoxLayout(self)
        self.mainLayout.addWidget(self.janitorsCombox)
        self.mainLayout.addWidget(self.resetFakeSceneBtn)
        self.mainLayout.addWidget(self.panelsWLayout)


        self.populateJanitors()
        self.populateJanitorsPanels()

        self.janitorsCombox.currentIndexChanged[int].connect(self.setCurrentJanitor)
        # self.allTasksCheckBox.stateChanged.connect(self.changeAllTasksActiveStatus)
        self.resetFakeSceneBtn.clicked.connect(self.resetFakeScene)

        self.setCurrentJanitor(0)

    def resetFakeScene(self):
        self.fakeScene.reset()

    def populateJanitors(self):


        janitorsList  = [janitorCmds.FacialJanitor,
                         janitorCmds.MarioFacialJanitor,
                         janitorCmds.ModelCharsJanitor,
                        ]
        self.janitors = [x(fakeScene=self.fakeScene) for x in janitorsList]

        self.janitorsCombox.clear()
        for janitor in self.janitors:
            self.janitorsCombox.addItem(janitor.niceName or janitor.__class__.__name__)


    def populateJanitorsPanels(self):
        self.janitorsPanels = []

        for janitor in self.janitors:
            panel = JanitorPanel(janitor)
            self.janitorsPanels.append(panel)
            self.panelsWLayout.addWidget(panel)


    def setCurrentJanitor(self, janitorIndex):
        # currentJanitor = self.janitors[janitorIndex]

        for i, panel in enumerate(self.janitorsPanels):
            vis = i == janitorIndex
            panel.setVisible(vis)





class FakeScene(object):
    def __init__(self):
        self.data = dict()
        self.reset()

    def reset(self):
        self.data['modelDoublons']       = ['|group1|body_msh', '|group2|body_msh']
        self.data['modelShaders']        = ['lambert1', 'lambert2']


        self.data['facialVersion']       = 4.1
        self.data['facialNastyRefEdits'] = ['ACTOR:spine.rotateOrder', 'ACTOR:neck.rotateOrder', 'ACTOR:head.rotateOrder']
        self.data['facialDkTags']        = ['EYES_AREA_CTRL_l_eye_blend', 'EYES_AREA_CTRL_r_eye_blend', 'EYES_AREA_CTRL_l_mouth_up']






if __name__=="__main__":

    # print(sys.version)
    # print(sys.path)
    app = QtGui.QApplication(sys.argv)

    janitor_ui = JanitorUi()
    janitor_ui.show()

    # janitor = janitorCmds.FacialJanitor()
    # janitorPanel = JanitorPanel(janitor)
    # janitorPanel.show()

    sys.exit(app.exec_())

