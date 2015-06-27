from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.FSM import FSM
from direct.distributed.PyDatagram import *
import semidbm
import time
import hmac
import hashlib
import json
from pirates.pirate.HumanDNA import HumanDNA


class LocalAccountDB:
    def __init__(self, csm):
        self.csm = csm

        # This uses dbm, so we open the DB file:
        filename = simbase.config.GetString('account-bridge-filename',
                                            'account-bridge')
        self.dbm = semidbm.open(filename, 'c')

    def lookup(self, cookie, callback):
        if cookie.startswith('.'):
            # Beginning a cookie with . symbolizes "invalid"
            callback({'success': False,
                      'reason': 'Invalid cookie specified!'})
            return

        # See if the cookie is in the DBM:
        if cookie in self.dbm:
            # Return it w/ account ID!
            callback({'success': True,
                      'databaseId': int(self.dbm[cookie]),
                      'accountId': cookie})
        else:
            # Nope, let's return w/o account ID:
            callback({'success': True,
                      'accountId': 0,
                      'databaseId': cookie})

    def storeAccountID(self, databaseId, accountId, callback):
        self.dbm[databaseId] = str(accountId)
        callback()

class RemoteAccountDB:
    def __init__(self, csm):
        self.csm = csm

        self.http = HTTPClient()
        self.http.setVerifySsl(0)

    def lookup(self, cookie, callback):
        response = self.__executeHttpRequest("verify/%s" % cookie, cookie)
        if (not response['status'] or not response['valid']): # status will be false if there's an hmac error, for example
            callback({'success': False,
                      'reason': response['banner']})
        else:
            gsUserId = response['gs_user_id']
            if (gsUserId == -1):
                gsUserId = 0
            callback({'success': True,
                      'accountId': response['user_id'],
                      'databaseId': gsUserId})

    def storeAccountID(self, databaseId, accountId, callback):
        response = self.__executeHttpRequest("associate_user/%s/with/%s" % (accountId, databaseId), str(accountId) + str(databaseId))
        if (not response['status']):
            self.csm.notify.warning("Unable to set databaseId with account server! Message: %s" % response['banner'])
            callback(False)
        else:
            callback(True)

    def __executeHttpRequest(self, url, message):
        channel = self.http.makeChannel(True)
        spec = DocumentSpec(simbase.config.GetString("account-server-endpoint", "https://www.piratesonline.com/api/gameserver/") + url)
        rf = Ramfile()
        digest = hmac.new(simbase.config.GetString('account-server-secret', 'dev'), message, hashlib.sha256)
        expiration = str((int(time()) * 1000) + 60000)
        digest.update(expiration)
        channel.sendExtraHeader('User-Agent', 'POTCO CSM bot')
        channel.sendExtraHeader('X-Gameserver-Signature', digest.hexdigest())
        channel.sendExtraHeader('X-Gameserver-Request-Expiration', expiration)
        channel.getDocument(spec)
        channel.downloadToRam(rf)
        return json.loads(rf.getData())

class OperationFSM(FSM):
    TARGET_CONNECTION = False

    def __init__(self, csm, target):
        self.csm = csm
        self.target = target

        FSM.__init__(self, self.__class__.__name__)

    def enterKill(self, reason=''):
        if self.TARGET_CONNECTION:
            self.csm.killConnection(self.target, reason)
        else:
            self.csm.killAccount(self.target, reason)
        self.demand('Off')

    def enterOff(self):
        if self.TARGET_CONNECTION:
            del self.csm.connection2fsm[self.target]
        else:
            del self.csm.account2fsm[self.target]

class LoginAccountFSM(OperationFSM):
    TARGET_CONNECTION = True
    notify = directNotify.newCategory('LoginAccountFSM')

    def enterStart(self, cookie):
        self.cookie = cookie

        self.demand('QueryAccountDB')

    def enterQueryAccountDB(self):
        self.csm.accountDB.lookup(self.cookie, self.__handleLookup)

    def __handleLookup(self, result):
        if not result.get('success'):
            self.demand('Kill', result.get('reason', 'The accounts database rejected your cookie.'))
            return

        self.databaseId = result.get('databaseId', 0)
        accountId = result.get('accountId', 0)
        if accountId:
            self.accountId = accountId
            self.demand('RetrieveAccount')
        else:
            self.demand('CreateAccount')

    def enterRetrieveAccount(self):
        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.databaseId,
                                             self.__handleRetrieve)

    def __handleRetrieve(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['AccountUD']:
            self.demand('Kill', 'Your account object was not found in the database!')
            return

        self.account = fields
        self.demand('SetAccount')

    def enterCreateAccount(self):
        self.account = {'ACCOUNT_AV_SET': [0]*6,
                        'pirateAvatars': [],
                        'HOUSE_ID_SET': [0]*6,
                        'ESTATE_ID': 0}

        self.csm.air.dbInterface.createObject(
            self.csm.air.dbId,
            self.csm.air.dclassesByName['AccountUD'],
            self.account,
            self.__handleCreate)

    def __handleCreate(self, accountId):
        if self.state != 'CreateAccount':
            self.notify.warning('Received create account response outside of CreateAccount state.')
            return

        if not accountId:
            self.notify.warning('Database failed to construct an account object!')
            self.demand('Kill', 'Your account object could not be created in the game database.')
            return

        self.accountId = accountId
        self.demand('StoreAccountID')

    def enterStoreAccountID(self):
        self.csm.accountDB.storeAccountID(self.databaseId, self.accountId, self.__handleStored)

    def __handleStored(self, success=True):
        if not success:
            self.demand('Kill', 'The account server could not save your account DB ID!')
            return

        self.demand('SetAccount')

    def enterSetAccount(self):
        # Sometimes databaseId becomes the cookie..
        if isinstance(self.databaseId, str):
            self.databaseId = self.accountId
            self.accountId = self.cookie

        # First, if there's anybody on the account, kill 'em for redundant login:
        dg = PyDatagram()
        dg.addServerHeader(self.csm.GetAccountConnectionChannel(int(self.databaseId)),
                           self.csm.air.ourChannel, CLIENTAGENT_EJECT)
        dg.addUint16(100)
        dg.addString('This account has been logged in elsewhere.')
        self.csm.air.send(dg)

        # Next, add this connection to the account channel.
        dg = PyDatagram()
        dg.addServerHeader(self.target, self.csm.air.ourChannel, CLIENTAGENT_OPEN_CHANNEL)
        dg.addChannel(self.csm.GetAccountConnectionChannel(self.databaseId))
        self.csm.air.send(dg)

        # Now set their sender channel to represent their account affiliation:
        dg = PyDatagram()
        dg.addServerHeader(self.target, self.csm.air.ourChannel, CLIENTAGENT_SET_CLIENT_ID)
        dg.addChannel(self.databaseId << 32) # accountId in high 32 bits, 0 in low (no avatar)
        self.csm.air.send(dg)

        # Un-sandbox them!
        dg = PyDatagram()
        dg.addServerHeader(self.target, self.csm.air.ourChannel, CLIENTAGENT_SET_STATE)
        dg.addUint16(2) # ESTABLISHED state. BIG FAT SECURITY RISK!!!
        self.csm.air.send(dg)

        # We're done.
        self.csm.sendUpdateToChannel(self.target, 'acceptLogin', [])
        self.demand('Off')


class CreateAvatarFSM(OperationFSM):
    notify = directNotify.newCategory('CreateAvatarFSM')

    def enterStart(self, dna, index):
        self.index = index
        self.dna = dna

        # Okay, we're good to go, let's query their account.
        self.demand('RetrieveAccount')

    def enterRetrieveAccount(self):
        self.csm.air.dbInterface.queryObject(
            self.csm.air.dbId, self.target, self.__handleRetrieve)

    def __handleRetrieve(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['AccountUD']:
            self.demand('Kill', 'Your account object was not found in the database!')
            return

        self.account = fields

        self.avList = self.account['ACCOUNT_AV_SET']
        # Sanitize:
        self.avList = self.avList[:6]
        self.avList += [0] * (6-len(self.avList))

        # Make sure the index is open:
        if self.avList[self.index]:
            self.demand('Kill', 'This avatar slot is already taken by another avatar!')
            return

        # Okay, there's space. Let's create the avatar!
        self.demand('CreateAvatar')

    def enterCreateAvatar(self):
        dna = HumanDNA()
        dna.makeFromNetString(self.dna)
        name = 'Test'
        pirateFields = {
            'setName': (name,),
            'WishNameState': ('',),
            'WishName': ('',),
            'setCompositeDNA': dna.getCompositeDNA(),
            'setDISLid': (self.target,)
        }
        self.csm.air.dbInterface.createObject(
            self.csm.air.dbId,
            self.csm.air.dclassesByName['DistributedPlayerPirateUD'],
            pirateFields,
            self.__handleCreate)

    def __handleCreate(self, avId):
        if not avId:
            self.demand('Kill', 'Database failed to create the new avatar object!')
            return

        self.avId = avId
        self.demand('StoreAvatar')

    def enterStoreAvatar(self):
        # Associate the avatar with the account...
        self.avList[self.index] = self.avId
        self.csm.air.dbInterface.updateObject(
            self.csm.air.dbId,
            self.target,
            self.csm.air.dclassesByName['AccountUD'],
            {'ACCOUNT_AV_SET': self.avList},
            {'ACCOUNT_AV_SET': self.account['ACCOUNT_AV_SET']},
            self.__handleStoreAvatar)

    def __handleStoreAvatar(self, fields):
        if fields:
            self.demand('Kill', 'Database failed to associate the new avatar to your account!')
            return

        # Otherwise, we're done!
        self.csm.air.writeServerEvent('avatarCreated', self.avId, self.target, self.dna.encode('hex'), self.index)
        self.csm.sendUpdateToAccountId(self.target, 'createAvatarResp', [self.avId])
        self.demand('Off')


class ClientServicesManagerUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory('ClientServicesManagerUD')

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)

        # These keep track of the connection/account IDs currently undergoing an
        # operation on the CSM. This is to prevent (hacked) clients from firing up more
        # than one operation at a time, which could potentially lead to exploitation
        # of race conditions.
        self.connection2fsm = {}
        self.account2fsm = {}

        # Instantiate our account DB interface using config:
        dbtype = simbase.config.GetString('accountdb-type', 'local')
        if dbtype == 'local':
            self.accountDB = LocalAccountDB(self)
        elif dbtype == 'remote':
            self.accountDB = RemoteAccountDB(self)
        else:
            self.notify.error('Invalid account DB type configured: %s' % dbtype)

    def killConnection(self, connId, reason):
        dg = PyDatagram()
        dg.addServerHeader(connId, self.air.ourChannel, CLIENTAGENT_EJECT)
        dg.addUint16(122)
        dg.addString(reason)
        self.air.send(dg)

    def killConnectionFSM(self, connId):
        fsm = self.connection2fsm.get(connId)
        if not fsm:
            self.notify.warning('Tried to kill connection %d for duplicate FSM, but none exists!' % connId)
            return
        self.killConnection(connId, 'An operation is already underway: ' + fsm.name)

    def killAccount(self, accountId, reason):
        self.killConnection(self.GetAccountConnectionChannel(accountId), reason)

    def killAccountFSM(self, accountId):
        fsm = self.account2fsm.get(accountId)
        if not fsm:
            self.notify.warning('Tried to kill account %d for duplicate FSM, but none exists!' % accountId)
            return
        self.killAccount(accountId, 'An operation is already underway: ' + fsm.name)

    def login(self, cookie):
        self.notify.debug('Received login cookie %r from %d' % (cookie, self.air.getMsgSender()))

        sender = self.air.getMsgSender()

        if sender>>32:
            # Oops, they have an account ID on their connection already!
            self.killConnection(sender, 'Client is already logged in.')
            return

        if sender in self.connection2fsm:
            self.killConnectionFSM(sender)
            return

        self.connection2fsm[sender] = LoginAccountFSM(self, sender)
        self.connection2fsm[sender].request('Start', cookie)

    def requestAvatars(self):
        self.notify.debug('Received avatar list request from %d' % (self.air.getMsgSender()))

        avs = []

        self.sendUpdateToChannel(self.air.getMsgSender(), 'setAvatars', [avs])

    def chooseAvatar(self, avId):
        pass

    def createAvatar(self, dna, index):
        self.runAccountFSM(CreateAvatarFSM, dna, index)

    def runAccountFSM(self, fsmtype, *args):
        sender = self.air.getAccountIdFromSender()

        if not sender:
            self.killAccount(sender, 'Client is not logged in.')

        if sender in self.account2fsm:
            self.killAccountFSM(sender)
            return

        self.account2fsm[sender] = fsmtype(self, sender)
        self.account2fsm[sender].request('Start', *args)
