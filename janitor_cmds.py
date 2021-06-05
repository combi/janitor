from collections import OrderedDict
import copy

class TaskBase(object):
    niceName    = 'TaskBase'
    description = 'This task probably does amazing things'

    def __init__(self, fakeScene):
        self.checkResult = None
        self.toFix       = None
        self.fixResult   = None

        # self.niceName    = self.__class__.__name__
        # self.description = 'This task probably does amazing things'
        self.fakeScene   = fakeScene

    def check(self, verbose=True):
        """ Must be implemented by the subclass """
        if verbose:
            print
            print 'Checking %s:' %self.niceName


    def fix(self, toFix=None, verbose=True):
        """ Must be implemented by the subclass, or set to None if the task cannot not have a fix """
        if verbose:
            print
            print 'Fixing %s:' %self.niceName


    def checkFixCheck(self, verbose=True):
        """ Will run the check and if a fix exists, will run the fix and a last check
            Returns errors found by each check pass.
        """
        errors_pass1 = None
        errors_pass2 = None

        self.check(verbose=verbose)
        errors_pass1 = copy.deepcopy(self.toFix)
        if self.fix:  # if a fixing function exists
            self.fix(toFix=self.toFix, verbose=verbose)
            self.check(verbose=verbose)
            errors_pass2 = copy.deepcopy(self.toFix)
        else:
            errors_pass2 = errors_pass1

        return (errors_pass1, errors_pass2)


class JanitorBase(object):
    niceName    = 'JanitorBase'
    description = 'This janitor will probably save you thousands of hours'

    def __init__(self, fakeScene=None, verbose=True):

        self.verbose  = verbose
        self.tasks    = []
        self.fakeScene = fakeScene

    def addTask(self, taskType, active=True):
        task = taskType(fakeScene=self.fakeScene)
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


    def checkFixCheck(self, skipInactives=False):
        errors = OrderedDict()
        for task in self.tasks:
            if skipInactives and not task.active:
                continue
            error = task.checkFixCheck(verbose=self.verbose)
            if error:
                errors[task.niceName] = error
        return errors



# ===================================================================
#  MODEL
# ===================================================================
class TaskDoublons(TaskBase):
    niceName    = 'Doublons'
    description = 'Recense les objets qui ont le meme nom.'

    def __init__(self, *args, **kwargs):
        super(TaskDoublons, self).__init__(*args, **kwargs)

        self.fix = None

    def check(self, verbose=False):
        super(TaskDoublons, self).check(verbose=False)

        if not self.fakeScene: return
        self.toFix = self.fakeScene.data.get('modelDoublons')

        self.checkResult = self.toFix
        print 'toFix =', self.toFix


class TaskShaders(TaskBase):
    niceName    = 'Shaders'
    description = 'Les shaders doivent doivent avoir "_MTL" comme suffixe.'

    def __init__(self, *args, **kwargs):
        super(TaskShaders, self).__init__(*args, **kwargs)

    def check(self, verbose=False):
        super(TaskShaders, self).check(verbose=False)
        self.toFix = []

        if not self.fakeScene: return
        sceneShaders = self.fakeScene.data.get('modelShaders', [])
        for shader in sceneShaders:
            if not shader.endswith('_mtl'):
                self.toFix.append(shader)

        self.checkResult = self.toFix
        print 'toFix =', self.toFix


    def fix(self, toFix=None, verbose=False):
        super(TaskShaders, self).fix(verbose=False)
        self.fixResult = []

        _toFix = toFix or self.toFix
        if not _toFix:
            return

        if not self.fakeScene: return

        sceneShaders = self.fakeScene.data.get('modelShaders', [])

        for item in _toFix:
            if item not in sceneShaders:
                print 'Warning, %s does not exist in scene' %item
            else:
                sceneShaders.remove(item)
                sceneShaders.append('%s_mtl' %item)
                self.fixResult.append(item)
        print('Fixed %s' %self.fixResult)




class ModelCharsJanitor(JanitorBase):
    niceName    = 'Model Chars'
    description = 'Will help diagnose Model Chars problems'

    def __init__(self, *args, **kwargs):
        super(ModelCharsJanitor, self).__init__(*args, **kwargs)
        # self.niceName = 'Model Chars'
        self.addTask(TaskDoublons)
        self.addTask(TaskShaders)


# ===================================================================
# FACIAL
# ===================================================================

class TaskFacialVersion(TaskBase):
    def __init__(self, *args, **kwargs):
        super(TaskFacialVersion, self).__init__(*args, **kwargs)
        self.niceName = 'Facial Version'
        self.description = 'Le facial devrait etre en version 4.2.'

    def check(self, verbose=False):
        super(TaskFacialVersion, self).check(verbose=False)
        self.toFix = []

        if not self.fakeScene: return
        facialVersion = self.fakeScene.data.get('facialVersion')
        if facialVersion is None:
            print 'WARNING, NO FAICAL FOUND'
        elif facialVersion < 4.2:
            self.toFix.append('FACIAL_ALL')

        self.checkResult = self.toFix
        print 'toFix =', self.toFix


    def fix(self, toFix=None, verbose=False):
        super(TaskFacialVersion, self).fix(verbose=False)
        self.fixResult = None
        _toFix = toFix or self.toFix
        if not _toFix:
            return

        if not self.fakeScene: return
        print('Fixed %s' %_toFix)
        self.fixResult = _toFix
        self.fakeScene.data['facialVersion'] = 4.2

class TaskFacialNastyRefEdits(TaskBase):
    def __init__(self, *args, **kwargs):
        super(TaskFacialNastyRefEdits, self).__init__(*args, **kwargs)
        self.niceName = 'Nasty Reference Edits'
        self.description = ''\
        'La scene de facial ne devrait pas contenir certains refEdits.\n'\
        'Ceux-ci peuvent etre dus a des bugs maya ou\n'\
        'dans l\'un de nos tools,\n'\
        'ou encore a des erreurs de manipulations.'

    def check(self, verbose=False):
        super(TaskFacialNastyRefEdits, self).check(verbose=False)

        if not self.fakeScene: return
        self.toFix = self.fakeScene.data.get('facialNastyRefEdits')

        self.checkResult = self.toFix
        print 'toFix =', self.toFix

    def fix(self, toFix=None, verbose=False):
        super(TaskFacialNastyRefEdits, self).fix(verbose=False)
        self.fixResult = []

        _toFix = toFix or self.toFix

        if not _toFix:
            return

        if not self.fakeScene: return

        nastyRefEdits = self.fakeScene.data.get('facialNastyRefEdits', [])

        for item in list(_toFix):
            if item not in nastyRefEdits:
                print 'Warning, no refEdit found as %s' %item
            else:
                nastyRefEdits.remove(item)
                self.fixResult.append(item)
        print('Fixed %s' %self.fixResult)

class TaskFacialDKsTag(TaskBase):
    def __init__(self, *args, **kwargs):
        super(TaskFacialDKsTag, self).__init__(*args, **kwargs)
        self.niceName = 'Driven Keys Tags'
        self.description = 'Les drivenKeys utilisees dans le facial devraient etre taggees'

    def check(self, verbose=False):
        super(TaskFacialDKsTag, self).check(verbose=False)

        if not self.fakeScene: return

        self.toFix = self.fakeScene.data.get('facialDkTags')
        self.checkResult = self.toFix
        print 'toFix =', self.toFix

    def fix(self, toFix=None, verbose=False):
        super(TaskFacialDKsTag, self).fix(verbose=False)
        self.fixResult = []
        _toFix = toFix or self.toFix

        if not _toFix:
            return

        if not self.fakeScene: return

        facialDks = self.fakeScene.data.get('facialDkTags', [])
        for item in list(_toFix):
            if item not in facialDks:
                print 'Warning, drivenKey %s does not exist' %item
            else:
                facialDks.remove(item)
                self.fixResult.append(item)
        print('Fixed %s' %self.fixResult)


class FacialJanitor(JanitorBase):
    movie = 'dm4'
    niceName    = 'Facial'
    description = 'Will help diagnose Facial Scene problems'

    def __init__(self, *args, **kwargs):
        super(FacialJanitor, self).__init__(*args, **kwargs)

        # self.niceName = 'Facial'

        self.addTask(TaskFacialVersion)
        self.addTask(TaskFacialNastyRefEdits)
        if self.movie == 'dm4': self.addTask(TaskFacialDKsTag)
        self.addTask(TaskDoublons)
        self.addTask(TaskShaders)



class MarioFacialJanitor(JanitorBase):
    niceName    = 'Facial (project Mario)'
    description = 'Will help diagnose Facial Scene problems on Mario project'

    def __init__(self, *args, **kwargs):
        super(MarioFacialJanitor, self).__init__(*args, **kwargs)





if __name__=="__main__":
    janitor = FacialJanitor(verbose=True)
    # janitor.check()
    # janitor.fix()
    print janitor.niceName

    janitor = FacialJanitor
    print janitor.niceName
