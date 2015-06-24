from direct.gui.DirectGui import *

from pirates.piratesgui import PiratesGuiGlobals
from pirates.piratesbase import PiratesGlobals
from pirates.piratesbase import PLocalizer
from pirates.piratesgui.BorderFrame import BorderFrame


class ChatWarningBox(BorderFrame):
    
    def __init__(self, badText = 'Error'):
        self.sizeX = 0.80000000000000004
        self.sizeZ = 0.59999999999999998
        textScale = PiratesGuiGlobals.TextScaleTitleSmall
        optiondefs = (('state', DGG.DISABLED, None), ('frameSize', (-0.0 * self.sizeX, 1.0 * self.sizeX, -0.0 * self.sizeZ, 1.0 * self.sizeZ), None), ('text', PLocalizer.ChatWarningTitle, None), ('text_align', TextNode.ACenter, None), ('text_font', PiratesGlobals.getPirateBoldOutlineFont(), None), ('text_fg', (1, 1, 1, 1), None), ('text_shadow', PiratesGuiGlobals.TextShadow, None), ('textMayChange', 1, None), ('text_scale', textScale, None), ('text_pos', (self.sizeX * 0.5, self.sizeZ - textScale * 1.5), None))
        self.defineoptions({ }, optiondefs)
        BorderFrame.__init__(self, parent = NodePath())
        self.initialiseoptions(ChatWarningBox)
        self.setX(self.sizeX * -0.5)
        self.badText = badText
        self.warningText = badText
        self.setup()

    
    def setup(self):
        self.setBin('gui-popup', 100)
        Gui = loader.loadModel('models/gui/toplevel_gui')
        buttonImage = (Gui.find('**/generic_button'), Gui.find('**/generic_button_down'), Gui.find('**/generic_button_over'), Gui.find('**/generic_button_disabled'))
        textScale = PiratesGuiGlobals.TextScaleLarge
        self.messageLabel = DirectLabel(parent = self, relief = None, text = self.warningText, text_font = PiratesGlobals.getPirateBoldOutlineFont(), text_align = TextNode.ALeft, text_scale = textScale, text_fg = PiratesGuiGlobals.TextFG2, text_shadow = PiratesGuiGlobals.TextShadow, text_wordwrap = self.sizeX * 0.90000000000000002 / textScale, text_pos = (self.sizeX * -0.42499999999999999, 0.066000000000000003), pos = (self.sizeX * 0.5, 0.0, self.sizeZ * 0.5))
        generic_x = Gui.find('**/generic_x')
        generic_box = Gui.find('**/generic_box')
        generic_box_over = Gui.find('**/generic_box_over')
        self.cancelButton = DirectButton(parent = self, relief = None, image = buttonImage, image_scale = (0.28000000000000003, 1.0, 0.22), image0_color = VBase4(0.65000000000000002, 0.65000000000000002, 0.65000000000000002, 1), image1_color = VBase4(0.40000000000000002, 0.40000000000000002, 0.40000000000000002, 1), image2_color = VBase4(0.90000000000000002, 0.90000000000000002, 0.90000000000000002, 1), image3_color = VBase4(0.40999999999999998, 0.40000000000000002, 0.40000000000000002, 1), text = PLocalizer.ChatWarningClose, text_font = PiratesGlobals.getPirateBoldOutlineFont(), text_align = TextNode.ACenter, text_pos = (0, -0.01), text_scale = PiratesGuiGlobals.TextScaleLarge, text_fg = PiratesGuiGlobals.TextFG2, text_shadow = PiratesGuiGlobals.TextShadow, pos = (self.sizeX * 0.5, 0, 0.10000000000000001), command = self.requestClose)

    
    def requestClose(self):
        self.close()
        localAvatar.guiMgr.closeSystemWarning()

    
    def close(self):
        self.destroy()


