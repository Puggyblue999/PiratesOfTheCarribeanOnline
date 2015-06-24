from direct.distributed.ClockDelta import *

from pirates.pirate import DistributedPirateBase
from pirates.battle import DistributedBattleNPC


class DistributedNPCPirate(DistributedBattleNPC.DistributedBattleNPC, DistributedPirateBase.DistributedPirateBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedNPCPirate')
    
    def __init__(self, cr):
        DistributedBattleNPC.DistributedBattleNPC.__init__(self, cr)
        DistributedPirateBase.DistributedPirateBase.__init__(self, cr)

    
    def disable(self):
        DistributedBattleNPC.DistributedBattleNPC.disable(self)
        DistributedPirateBase.DistributedPirateBase.disable(self)
        self.stopBlink()
        self.ignoreAll()

    
    def delete(self):
        
        try:
            pass
        except:
            self.DistributedNPCPirate_deleted = 1
            DistributedBattleNPC.DistributedBattleNPC.delete(self)
            DistributedPirateBase.DistributedPirateBase.delete(self)


    
    def generate(self):
        DistributedBattleNPC.DistributedBattleNPC.generate(self)
        DistributedPirateBase.DistributedPirateBase.generate(self)
        self.setInteractOptions(proximityText = None, allowInteract = False)

    
    def announceGenerate(self):
        DistributedBattleNPC.DistributedBattleNPC.announceGenerate(self)
        DistributedPirateBase.DistributedPirateBase.announceGenerate(self)

    
    def setDNAString(self, dnaString):
        DistributedPirateBase.DistributedPirateBase.setDefaultDNA(self)
        self.style.makeNPCPirate()

    
    def isBattleable(self):
        return 0

    
    def play(self, *args, **kwArgs):
        Pirate.Pirate.play(self, *args, **args)

    
    def loop(self, *args, **kwArgs):
        Pirate.Pirate.loop(self, *args, **args)

    
    def pose(self, *args, **kwArgs):
        Pirate.Pirate.pose(self, *args, **args)

    
    def pingpong(self, *args, **kwArgs):
        Pirate.Pirate.pingpong(self, *args, **args)

    
    def stop(self, *args, **kwArgs):
        Pirate.Pirate.stop(self, *args, **args)


