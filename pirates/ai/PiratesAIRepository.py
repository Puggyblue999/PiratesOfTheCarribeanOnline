from pandac.PandaModules import *
from direct.distributed.PyDatagram import *
from pirates.distributed.PiratesInternalRepository import PiratesInternalRepository
from pirates.distributed.PiratesDistrictAI import PiratesDistrictAI
from pirates.world.WorldCreatorAI import WorldCreatorAI
from otp.ai.TimeManagerAI import TimeManagerAI
from otp.distributed.OtpDoGlobals import *


class PiratesAIRepository(PiratesInternalRepository):
    def __init__(self, baseChannel, stateServerChannel, districtName):
        PiratesInternalRepository.__init__(
            self, baseChannel, stateServerChannel, dcSuffix='AI')

        self.districtName = districtName

        self.notify.setInfo(True)

    def createManagers(self):
        self.timeManager = TimeManagerAI(self)
        self.timeManager.generateWithRequired(2)

    def createWorlds(self):
        self.worldCreator = WorldCreatorAI(self, None, self.distributedDistrict)
        self.worldCreator.makeMainWorld('PortRoyalIsland.py')
        print self.worldCreator.world

    def handleConnected(self):
        self.districtId = self.allocateChannel()
        self.notify.info('Creating PiratesDistrictAI(%d)...' % self.districtId)
        self.distributedDistrict = PiratesDistrictAI(self)
        self.distributedDistrict.setName(self.districtName)
        self.distributedDistrict.generateWithRequiredAndId(
            self.districtId, OTP_DO_ID_PIRATES, OTP_ZONE_ID_DISTRICTS)
        self.notify.info('Claiming ownership of channel ID: %d...' % self.districtId)
        self.claimOwnership(self.districtId)

        self.notify.info('Creating worlds...')
        self.createWorlds()

        self.notify.info('Creating managers...')
        self.createManagers()

        self.notify.info('Making district available...')
        self.distributedDistrict.b_setAvailable(1)
        self.notify.info('Done.')

    def claimOwnership(self, channelId):
        datagram = PyDatagram()
        datagram.addServerHeader(channelId, self.ourChannel,
                                 STATESERVER_OBJECT_SET_AI)
        datagram.addChannel(self.ourChannel)
        self.send(datagram)