class TaskBase(object):
    def __init__(self):
        self.checkResult = None
        self.toFix       = None
        self.fixResult   = None

        self.niceName    = self.__class__.__name__
        self.description = 'TaskBase does amazing things'


    def check(self, verbose=True):
        if verbose:
            print
            print 'Checking %s:' %self.niceName
            # print 'checkResult =', self.checkResult


    def fix(self, toFix=None, verbose=True):
        if verbose:
            print
            print 'Fixing %s:' %self.niceName


    def checkAndFix(self, verbose=True):
        self.check(verbose=verbose)
        self.fix(toFix=self.toFix, verbose=verbose)


class JanitorBase(object):
    def __init__(self, verbose=True):

        self.verbose  = verbose
        self.tasks    = []
        self.niceName = ''

    def addTask(self, taskType, active=True):
        print 'adding task %s' %taskType
        task = taskType()
        self.tasks.append(task)
        task.active = active

    def check(self):
        if self.verbose:
            msg = 'Running checks of %s' %self.niceName or self.__class__.__name__
            print
            print '-'*len(msg)
            print msg
            print '-'*len(msg)

        for task in self.tasks:
            if not task.active:
                continue
            # print '  Running check ', task
            task.check(verbose=self.verbose)


    def fix(self):
        if self.verbose:
            msg = 'Running fixes of %s' %self.niceName or self.__class__.__name__  # faire une property
            print
            print '-'*len(msg)
            print msg
            print '-'*len(msg)

        for task in self.tasks:
            if not task.active:
                continue
            task.fix(task.toFix, verbose=self.verbose)





# ===================================================================
#  MODEL
# ===================================================================
class TaskDoublons(TaskBase):
    def __init__(self, verbose=True):
        super(TaskDoublons, self).__init__()
        self.niceName = 'Doublons'

    def check(self, verbose=True):
        super(TaskDoublons, self).check()
        self.toFix = ['|group1|body_msh', '|group2|body_msh']
        self.checkResult = self.toFix

class TaskShaders(TaskBase):
    def __init__(self, verbose=True):
        super(TaskShaders, self).__init__()
        self.niceName = 'Shaders'

    def check(self, verbose=True):
        super(TaskShaders, self).check()
        self.toFix = ['lambert1', 'lambert2']
        self.checkResult = self.toFix




class ModelCharsJanitor(JanitorBase):
    def __init__(self, verbose=True):
        super(ModelCharsJanitor, self).__init__(verbose=verbose)
        self.niceName = 'Model Chars'
        self.addTask(TaskDoublons)
        self.addTask(TaskShaders)


# ===================================================================
# FACIAL
# ===================================================================

class TaskFacialVersion(TaskBase):
    def __init__(self, verbose=True):
        super(TaskFacialVersion, self).__init__()
        self.niceName = 'Facial Version'

    def check(self, verbose=True):
        super(TaskFacialVersion, self).check()
        result = 4.2
        if result <= 4.2:
            self.toFix = 'FACIAL_ALL'
        self.checkResult = result
        print 'self.checkResult =', self.checkResult

    def fix(self, toFix=None, verbose=True):
        super(TaskFacialVersion, self).fix()
        self.fixResult = None
        if not toFix:
            return
        if verbose:
            print('updating %s to version 4.2' %self.toFix)


class TaskFacialNastyRefEdits(TaskBase):
    def __init__(self, verbose=True):
        super(TaskFacialNastyRefEdits, self).__init__()
        self.niceName = 'Nasty Reference Edits'

    def check(self, verbose=True):
        super(TaskFacialNastyRefEdits, self).check()
        result = None
        toFix  = None
        if True:
            toFix  = ['ACTOR:HEAD.rotateOrder']
            result = list(toFix)

        self.checkResult = result
        self.toFix       = toFix
        print 'self.checkResult =', self.checkResult


    def fix(self, toFix=None, verbose=True):
        super(TaskFacialNastyRefEdits, self).fix()
        self.fixResult = None
        _toFix = toFix or self.toFix
        if not _toFix:
            return
        if verbose:
            print('Removing following refEdits:')
            for x in _toFix:
                print(x)
        self.toFix = None


class TaskFacialDKsTag(TaskBase):
    def __init__(self, verbose=True):
        super(TaskFacialDKsTag, self).__init__()
        self.niceName = 'Driven Keys Tags'

    def check(self, verbose=True):
        super(TaskFacialDKsTag, self).check()
        result = None
        toFix  = None

        if True:
            toFix = ['EYES_AREA_CTRL_l_eye_blend']
            result = list(toFix)

        self.checkResult = result
        self.toFix       = toFix


    def fix(self, toFix=None, verbose=True):
        super(TaskFacialDKsTag, self).fix()
        self.fixResult = None
        if not toFix:
            return
        if verbose:
            for x in self.toFix:
                print('Tagging %s' %x)

class FacialJanitor(JanitorBase):
    movie = 'dm4'
    # movie = 'mig'

    def __init__(self, verbose=True):
        super(FacialJanitor, self).__init__(verbose=verbose)
        self.niceName = 'Facial'

        self.addTask(TaskFacialVersion)
        self.addTask(TaskFacialNastyRefEdits)
        if self.movie == 'dm4': self.addTask(TaskFacialDKsTag)
        self.addTask(TaskDoublons)
        self.addTask(TaskShaders)



class MarioFacialJanitor(JanitorBase):

    def __init__(self, verbose=True):
        super(MarioFacialJanitor, self).__init__(verbose=verbose)
        self.niceName = 'Mario Facial'





if __name__=="__main__":
    janitor = FacialJanitor(verbose=True)
    janitor.check()
    # janitor.fix()

