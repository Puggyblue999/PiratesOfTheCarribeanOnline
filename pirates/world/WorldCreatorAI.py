from pirates.world.WorldCreatorBase import WorldCreatorBase
from direct.directnotify.DirectNotifyGlobal import *
from pirates.piratesbase import PiratesGlobals

class WorldCreatorAI(WorldCreatorBase):
    notify = directNotify.newCategory('WorldCreatorAI')

    def __init__(self, air, worldFile, district):
        self.fileDicts = {}
        self.world = None
        WorldCreatorBase.__init__(self, air, worldFile)
        self.air = air
        self.district = district


    def makeMainWorld(self, worldFile):
        self.worldType = PiratesGlobals.INSTANCE_MAIN
        if worldFile is not None:
            fileDict, objects = self.loadObjectsFromFile(worldFile, self.repository)

        self.worldType = None

    def loadObject(self, object, parent, parentUid, objKey, dynamic, parentIsObj = False, fileName = None, actualParentObj = None):
        prevWorld = self.world
        newObjInfo = self.createObject(
            object, parent, parentUid, objKey, dynamic,
            parentIsObj = parentIsObj, fileName = fileName, actualParentObj = actualParentObj)

        if newObjInfo:
            if len(newObjInfo) == 2:
                (newObj, newActualParent) = newObjInfo
            else:
                newObj = newObjInfo
                newActualParent = self.air
        else:
            return None
        instanced = object.get('Instanced')
        if instanced:
            self.world.setCanBePrivate(instanced)

        objDict = object.get('Objects')
        if objDict:
            if newObj == None:
                newObj = parent
                if hasattr(newObj, 'getUniqueId'):
                    objKey = newObj.getUniqueId()


            self.loadObjectDict(objDict, newObj, objKey, dynamic, fileName = fileName, actualParentObj = newActualParent)

        self._restoreWorld(prevWorld)
        return newObj

    def createObject(self, object, parent, parentUid, objKey, dynamic, parentIsObj = False, fileName = None, actualParentObj = None):
        objType = object.get('Type')
        self.notify.debug('createObject: type = %s' % objType)
        if dynamic and object.get('ExtUid'):
            return objType

        childFilename = object.get('File')
        if childFilename and object['Type'] != 'Building Exterior' and object['Type'] != 'Island Game Area':
            self.loadObjectsFromFile(childFilename + '.py', parent)
            return None

        return objType

