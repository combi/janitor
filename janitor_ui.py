import sys
import random
from collections import OrderedDict

from PySide import QtGui
from PySide import QtCore

import janitor_cmds as janitorCmds
import coreUtils

print coreUtils
class Colors():
    red           = QtGui.QColor(120,   0,   0)
    green         = QtGui.QColor(000, 120,   0)
    blue          = QtGui.QColor(100, 100, 220)
    orange        = QtGui.QColor(200, 100,   0)
    yellow        = QtGui.QColor(255, 255,   0)

    green_dim     = QtGui.QColor(050,  90,  50)
    orange_dim    = QtGui.QColor(100,  50,  50)
    blue_dim      = QtGui.QColor(50,  50, 110)
    yellow_dim    = QtGui.QColor(180, 180,   0)

    grey          = QtGui.QColor(100, 100, 100)
    darkGrey      = QtGui.QColor(050,  50,  50)
    darkerGrey    = QtGui.QColor(040,  40,  40)
    black         = QtGui.QColor(000,   0,   0)


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

    def setmargins(self, left=0, top=0, right=0, bottom=0):
        self.layout.setContentsMargins(left, top, right, bottom)



class TaskWidget(QtGui.QWidget):
    activeStateChanged = QtCore.Signal()

    def __init__(self, task, parent=None):
        super(TaskWidget, self).__init__(parent=parent)
        self.task = task

        self.checkBox    = QtGui.QCheckBox()
        self.checkButton = QtGui.QPushButton(task.niceName or '')
        self.fixButton   = QtGui.QPushButton('fix')
        self.helpButton  = QtGui.QPushButton('?')

        if task.active:
            self.checkBox.setCheckState(QtCore.Qt.Checked)
        else:
            self.checkBox.setCheckState(QtCore.Qt.Unchecked)

        self.layout = QtGui.QHBoxLayout(self)
        self.layout.addWidget(self.checkBox)
        self.layout.addWidget(self.checkButton)
        self.layout.addWidget(self.fixButton)
        self.layout.addWidget(self.helpButton)
        self.setLayout(self.layout)

        self.layout.setContentsMargins(5, 0, 5, 0)
        self.checkBox.setFixedWidth(15)
        self.fixButton.setFixedWidth(25)
        self.helpButton.setFixedWidth(25)
        self.helpButton.setFixedHeight(25)

        self.checkButton.clicked.connect(self.taskCheck)
        self.fixButton.clicked.connect(self.taskFix)
        self.checkBox.stateChanged.connect(self.setTaskActive)


    def taskCheck(self):
        self.task.check()

    def taskFix(self):
        self.task.fix()

    def setTaskActive(self, state):
        if state > 0:
            self.task.active = True
        else:
            self.task.active = False
        self.activeStateChanged.emit()



class JanitorWidget(QtGui.QWidget):
    def __init__(self, janitor, parent=None):
        super(JanitorWidget, self).__init__(parent=parent)
        self.janitor      = janitor
        self.tasksWidgets = []


        self.layout = QtGui.QVBoxLayout(self)
        headerWLayout = LayoutWidget(mode='horizontal', parent=self)
        panelWLayout  = LayoutWidget(mode='vertical', parent=self)

        headerWLayout.setContentsMargins(5, 0, 5, 10)
        setBgCol(headerWLayout, randomColor())
        setBgCol(panelWLayout, randomColor())

        self.mainCheckBox     = QtGui.QCheckBox()
        self.mainLaunchButton = QtGui.QPushButton('GO')
        self.mainFixButton    = QtGui.QPushButton('fix')

        self.mainCheckBox.setFixedWidth(15)
        self.mainFixButton.setFixedWidth(25)



        headerWLayout.addWidget(self.mainCheckBox)
        headerWLayout.addWidget(self.mainLaunchButton)
        headerWLayout.addWidget(self.mainFixButton)
        # headerWLayout.layout.addStretch()
        headerWLayout.layout.addSpacing(30)

        self.layout.addWidget(headerWLayout)
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
        # self.mainLaunchButton.clicked.connect(self.debug)

    def mainLaunch(self):
        self.debug()
        self.janitor.check()

    def debug(self):
        tasks = [taskWidget.task for taskWidget in self.tasksWidgets]
        states = OrderedDict([(task.niceName,task.active) for task in tasks])
        print
        print 'states =', states
        print coreUtils.buildSmartPrintStr(states)


    def updateMainCheckBoxState(self):
        self.mainCheckBox.blockSignals(True)
        tasksStates = [task.active for task in self.janitor.tasks]
        if all(tasksStates):
            print 'all tasks are active'
            self.mainCheckBox.setCheckState(QtCore.Qt.Checked)
            self.mainCheckBox.setTristate(False)
        elif any(tasksStates):
            print 'some tasks are active'
            self.mainCheckBox.setCheckState(QtCore.Qt.PartiallyChecked)
            self.mainCheckBox.setTristate(True)
        else:
            print 'no tasks are active'
            self.mainCheckBox.setCheckState(QtCore.Qt.Unchecked)
            self.mainCheckBox.setTristate(False)

        print 'isTriState:',  self.mainCheckBox.isTristate()
        self.mainCheckBox.blockSignals(False)

    def changeAllTasksActiveStatus(self, arg):
        print 'arg =', arg
        print 'isTriState:',  self.mainCheckBox.isTristate()

        checkState = QtCore.Qt.Checked if arg > 0 else QtCore.Qt.Unchecked
        for taskWidget in self.tasksWidgets:
            taskWidget.blockSignals(True)
            print 'taskWidget =', taskWidget
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

        # top part with conbobox and checkBox and go button
        # self.janitorsWLayout = LayoutWidget(mode='horizontal', parent=self)

        # self.allTasksCheckBox = QtGui.QCheckBox()
        self.janitorsCombox   = QtGui.QComboBox(parent=self)

        # self.janitorsWLayout.addWidget(self.allTasksCheckBox)
        # self.janitorsWLayout.addWidget(self.janitorsCombox)

        # self.allTasksCheckBox.setFixedWidth(15)
        # self.janitorsWLayout.setContentsMargins(5, 0, 5, 10)


        # Bottom part where all task button will go
        self.panelsWLayout   = LayoutWidget(mode='vertical', parent=self)


        # main layout
        self.mainLayout = QtGui.QVBoxLayout(self)
        self.mainLayout.addWidget(self.janitorsCombox)
        self.mainLayout.addWidget(self.panelsWLayout)




        self.populateJanitors()
        self.populateJanitorsPanels()

        self.janitorsCombox.currentIndexChanged[int].connect(self.setCurrentJanitor)
        # self.allTasksCheckBox.stateChanged.connect(self.changeAllTasksActiveStatus)

        self.setCurrentJanitor(0)


    def populateJanitorsPanels(self):
        self.janitorsPanels = []

        for janitor in self.janitors:
            panel = JanitorWidget(janitor)
            self.janitorsPanels.append(panel)
            self.panelsWLayout.addWidget(panel)


    def populateJanitors(self):
        janitorsList  = [janitorCmds.FacialJanitor,
                         janitorCmds.ModelCharsJanitor,
                        ]

        self.janitors       = [x() for x in janitorsList]

        self.janitorsCombox.clear()
        for janitor in self.janitors:
            self.janitorsCombox.addItem(janitor.niceName or janitor.__class__.__name__)

    def setCurrentJanitor(self, janitorIndex):
        # currentJanitor = self.janitors[janitorIndex]

        for i, panel in enumerate(self.janitorsPanels):
            vis = i == janitorIndex
            panel.setVisible(vis)


    def onTaskCheck(self):
        sender = self.sender()
        sender.task.check()

if __name__=="__main__":


    app = QtGui.QApplication(sys.argv)

    janitor_ui = JanitorUi()
    janitor_ui.show()

    # janitor = janitorCmds.FacialJanitor()
    # janitorPanel = JanitorWidget(janitor)
    # janitorPanel.show()

    sys.exit(app.exec_())

