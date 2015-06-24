# File: D (Python 2.4)

from direct.distributed import DistributedObject

class DistributedLootManager(DistributedObject.DistributedObject):
    
    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)

    
    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        base.cr.lootMgr = self

    
    def disable(self):
        DistributedObject.DistributedObject.disable(self)
        base.cr.lootMgr = None

    
    def delete(self):
        DistributedObject.DistributedObject.disable(self)

    
    def d_requestItemFromContainer(self, containerId, itemInfo):
        self.sendUpdate('requestItemFromContainer', [
            containerId,
            itemInfo])

    
    def d_requestItems(self, containers):
        self.sendUpdate('requestItems', [
            containers])

    
    def removeLootContainerFromScoreboard(self, containerId):
        if hasattr(base, 'localAvatar') and base.localAvatar.guiMgr:
            scoreboard = base.localAvatar.guiMgr.scoreboard
            if scoreboard and hasattr(scoreboard, 'removeLootContainer'):
                scoreboard.removeLootContainer(containerId)
            
        


