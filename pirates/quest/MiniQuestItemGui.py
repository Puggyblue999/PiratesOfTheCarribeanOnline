from direct.gui.DirectGui import *

from pirates.piratesgui import PiratesGuiGlobals


class MiniQuestItemGui(DirectFrame):
    Width = PiratesGuiGlobals.ObjectivesPanelWidth - PiratesGuiGlobals.GridSize
    Height = 0.10000000000000001
    
    def __init__(self, quest, parent = None, **kw):
        optiondefs = (('state', DGG.NORMAL, None), ('frameColor', PiratesGuiGlobals.FrameColor, None), ('borderWidth', PiratesGuiGlobals.BorderWidth, None), ('frameSize', (0.0, MiniQuestItemGui.Width, 0.0, MiniQuestItemGui.Height), None))
        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, parent)
        self.initialiseoptions(MiniQuestItemGui)
        self.quest = quest
        self._createIface()
        self.accept(self.quest.getChangeEvent(), self.handleQuestChange)

    
    def destroy(self):
        self._destroyIface()
        DirectFrame.destroy(self)
        del self.quest
        self.ignoreAll()

    
    def _createIface(self):
        if self.quest.isComplete():
            textFg = (0.10000000000000001, 0.80000000000000004, 0.10000000000000001, 1)
        else:
            textFg = PiratesGuiGlobals.TextFG1
        self.descText = DirectLabel(parent = self, relief = None, text = self.quest.getStatusText(), text_align = TextNode.ALeft, text_scale = PiratesGuiGlobals.TextScaleLarge, text_fg = textFg, text_shadow = PiratesGuiGlobals.TextShadow, textMayChange = 1, pos = (0.040000000000000001, 0, 0.050000000000000003))

    
    def _destroyIface(self):
        self.descText.destroy()
        del self.descText

    
    def handleQuestChange(self):
        self._destroyIface()
        self._createIface()


