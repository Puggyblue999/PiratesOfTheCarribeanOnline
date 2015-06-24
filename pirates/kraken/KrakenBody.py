from pirates.creature.Creature import Creature
from pirates.piratesbase import PiratesGlobals


class bp:
    kraken = bpdb.bpPreset(cfg = 'kraken', static = 1)


class KrakenBody(Creature):
    ModelInfo = ('models/char/live_kraken_zero', 'models/char/live_kraken_zero')
    AnimList = { }
    
    def __init__(self):
        Creature.__init__(self)
        self.enableMixing()
        self.collideBattleMask = PiratesGlobals.TargetBitmask | PiratesGlobals.BattleAimBitmask

    
    def setupCollisions(self):
        coll = CollisionSphere((0, 0, 0), 1)
        cn = CollisionNode('KrakenCollisions')
        cn.addSolid(coll)
        self.collision = self.attachNewNode(cn)
        self.collision.node().setIntoCollideMask(self.collideBattleMask)
        self.collision.setScale(100)
        self.collision.setZ(-80)
        self.collision.flattenStrong()

    
    def generateCreature(self):
        self.loadModel(ModelInfo[0])


