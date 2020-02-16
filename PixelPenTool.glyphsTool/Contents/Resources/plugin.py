# encoding: utf-8

###########################################################################################################
#
#
#	Select Tool Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/SelectTool
#
#
###########################################################################################################

from __future__ import division, print_function, unicode_literals
import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
import vanilla
import math

# PenTool = objc.lookUpClass("PenTool")
# class PixelPenTool(PenTool):
class PixelPenTool(SelectTool):
	
	@objc.python_method
	def settings(self):
		self.name = Glyphs.localize({'en': u'Pixel Pen Tool'})
		self.generalContextMenus = [
			{'name': Glyphs.localize({'en': u'Pixel Font Setup...'}), 'action': self.initialise},
		]
		self.keyboardShortcut = 'x'
		self.PixelPenWriteMode = False

	
	@objc.python_method
	def start(self):
		pass
	
	@objc.python_method
	def activate(self):
		if not Glyphs.font.userData["PixelPenSetup"]:
			InitialisePanel()
	
	@objc.python_method
	def background(self, layer):
		# Draw a red rectangle behind the glyph as big as the glyph’s bounding box
		# NSColor.redColor().set()
		# NSBezierPath.fillRect_(layer.bounds)
		pass
	
	@objc.python_method
	def deactivate(self):
		pass
	
	@objc.python_method
	def conditionalContextMenus(self):

		# Empty list of context menu items
		contextMenus = []

		# Execute only if layers are actually selected
		if Glyphs.font.selectedLayers:
			layer = Glyphs.font.selectedLayers[0]
			
			# Exactly one object is selected and it’s an anchor
			if len(layer.selection) == 1 and type(layer.selection[0]) == GSAnchor:
					
				# Add context menu item
				contextMenus.append({'name': Glyphs.localize({'en': u'Randomly move anchor', 'de': u'Anker zufällig verschieben'}), 'action': self.randomlyMoveAnchor})

		# Return list of context menu items
		return contextMenus
	
	@objc.python_method
	def initialise(self):
		InitialisePanel()

	@objc.python_method
	def mouseDown_(self, theEvent):
		if self.isCompoHere()[0] == True: # there is existing compo, it'll be the Eraser mode
			self.PixelPenWriteMode = False
		else:
			self.PixelPenWriteMode = True
		Glyphs.font.selectedLayers[0].parent.beginUndo()
		self.writeOrErase()

	@objc.python_method
	def mouseDragged_(self, theEvent):
		self.writeOrErase()
	
	@objc.python_method
	def mouseUp_(self, theEvent):
		Glyphs.font.selectedLayers[0].parent.endUndo()

	@objc.python_method
	def mousePosition(self):
		view = Glyphs.font.currentTab.graphicView()
		mousePosition = view.getActiveLocation_(Glyphs.currentEvent())
		return mousePosition

	@objc.python_method
	def compoPosAtMousePos(self):	
		mousePos = self.mousePosition()
		mousePosX = int(round(mousePos[0]))
		mousePosY = int(round(mousePos[1]))
		gri = Glyphs.font.grid
		finalX = int(mousePosX/gri)*gri if mousePosX >= 0 else math.floor(mousePosX/gri)*gri
		finalY = int(mousePosY/gri)*gri if mousePosY >= 0 else math.floor(mousePosY/gri)*gri
		return finalX, finalY

	@objc.python_method
	def isCompoHere(self):
		mousePos = self.mousePosition()
		possibleCompoX, possibleCompoY = self.compoPosAtMousePos()
		for c in Glyphs.font.selectedLayers[0].components:
			if c.x == possibleCompoX and c.y == possibleCompoY:
				return True, c
				break
		return False, False
	
	@objc.python_method
	def writeOrErase(self):
		if self.PixelPenWriteMode == True and self.isCompoHere()[0] == False: # drawing
			newCompo = GSComponent("_pixel")
			newCompo.name = "_pixel"
			newCompo.automaticAlignment = False
			newCompo.position = self.compoPosAtMousePos()
			Glyphs.font.selectedLayers[0].components.append(newCompo)

		elif self.PixelPenWriteMode == False and self.isCompoHere()[0] == True: # erasing
			Glyphs.font.selectedLayers[0].removeComponent_(self.isCompoHere()[1])

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__


GSSteppingTextField = objc.lookUpClass("GSSteppingTextField")
class ArrowEditText (vanilla.EditText):
	nsTextFieldClass = GSSteppingTextField
	def _setCallback(self, callback):
		super(ArrowEditText, self)._setCallback(callback)
		if callback is not None and self._continuous:
			self._nsObject.setContinuous_(True)
			self._nsObject.setAction_(self._target.action_)
			self._nsObject.setTarget_(self._target)

class InitialisePanel( object ):

	def __init__( self ):
		# Window 'self.w':
		edX = 40
		edY = 22
		txX = 75
		txY = 17
		sp = 10
		btnX = 60
		btnY = 22
		windowWidth  = sp*4+txX+edX+40
		windowHeight = sp*7+edY*7+btnY

		self.w = vanilla.FloatingWindow(
			posSize = ( 200, 100,windowWidth, windowHeight ), # default window size
			title = "Pixel Font Setup", # window title
			closable = False,
		)
		
		self.w.prevSettings = {
			"upm" : Glyphs.font.upm,
			"gri" : Glyphs.font.grid,
			"asc" : Glyphs.font.selectedFontMaster.ascender,
			"cap" : Glyphs.font.selectedFontMaster.capHeight,
			"xhe" : Glyphs.font.selectedFontMaster.xHeight,
			"des" : Glyphs.font.selectedFontMaster.descender }

		if not Glyphs.font.userData["PixelPenSetup"]:
			UIparam = {
				"gri" : 100,
				"asc" : 7,
				"cap" : 7,
				"xhe" : 5,
				"des" : -1 }
		else:
			UIparam = {
				"gri" : int(self.w.prevSettings["gri"]),
				"asc" : int( self.w.prevSettings["asc"] / self.w.prevSettings["gri"]),
				"cap" : int( self.w.prevSettings["cap"] / self.w.prevSettings["gri"]),
				"xhe" : int( self.w.prevSettings["xhe"] / self.w.prevSettings["gri"]),
				"des" : int( self.w.prevSettings["des"] / self.w.prevSettings["gri"]) }

		self.w.text_gri = vanilla.TextBox( (sp, sp, txX, txY), "Pixel Size" )
		self.w.edit_gri = ArrowEditText( (sp*2+txX, sp, edX, edY), UIparam["gri"], callback=self.refreshScreen)
		self.w.unit_gri = vanilla.TextBox( (sp*3+txX+edX, sp, txX, txY), "Units" )
		
		self.w.text_asc = vanilla.TextBox( (sp, sp*2+edY*1, txX, txY), "Ascender Height" )
		self.w.edit_asc = ArrowEditText( (sp*2+txX, sp*2+edY*1, edX, edY), UIparam["asc"], callback=self.refreshScreen)
		self.w.unit_asc = vanilla.TextBox( (sp*3+txX+edX, sp*2+edY*1, txX, txY), "Pixels" )

		self.w.text_cap = vanilla.TextBox( (sp, sp*3+edY*2, txX, txY), "Cap Height" )
		self.w.edit_cap = ArrowEditText( (sp*2+txX, sp*3+edY*2, edX, edY), UIparam["cap"], callback=self.refreshScreen)
		self.w.unit_cap = vanilla.TextBox( (sp*3+txX+edX, sp*3+edY*2, txX, txY), "Pixels" )

		self.w.text_xhe = vanilla.TextBox( (sp, sp*4+edY*3, txX, txY), "x Height" )
		self.w.edit_xhe = ArrowEditText( (sp*2+txX, sp*4+edY*3, edX, edY), UIparam["xhe"], callback=self.refreshScreen)
		self.w.unit_xhe = vanilla.TextBox( (sp*3+txX+edX, sp*4+edY*3, txX, txY), "Pixels" )

		self.w.text_des = vanilla.TextBox( (sp, sp*5+edY*4, txX, txY), "Descender Height" )
		self.w.edit_des = ArrowEditText( (sp*2+txX, sp*5+edY*4, edX, edY), UIparam["des"], callback=self.refreshScreen)
		self.w.unit_des = vanilla.TextBox( (sp*3+txX+edX, sp*5+edY*4, txX, txY), "Pixels" )

		self.w.text_upm = vanilla.TextBox( (sp, sp*6+edY*5, -sp, txY), "UPM will be set to : %s" % (UIparam["asc"]-UIparam["des"])*UIparam["gri"] )

		# Run Button:
		self.w.cancelButton = vanilla.Button((-sp*2-btnX*2, -sp-btnY, btnX, btnY), "Cancel", sizeStyle='regular', callback=self.CancelInitialise )
		self.w.runButton = vanilla.Button((-sp-btnX, -sp-btnY, btnX, btnY), "OK", sizeStyle='regular', callback=self.InitialisePanelMain )
		self.w.setDefaultButton( self.w.runButton )

		self.w.open()
		self.w.makeKey()
		self.refreshScreen(self.w.edit_gri)

	def InitialisePanelMain(self, sender):

		if not Glyphs.font.glyphs["_pixel"]:
			ng = GSGlyph()
			ng.name = "_pixel"
			Glyphs.font.glyphs.append(ng)

		newPixel = GSPath()
		pixSize = int(self.w.edit_gri.get())
		nodesList = ( (0,0), (pixSize, 0), (pixSize, pixSize), (0,pixSize) )
		for n in nodesList:
			newNode = GSNode()
			newNode.position = n
			newNode.type = GSLINE
			newNode.connection = 0
			newPixel.nodes.append(newNode)
		newPixel.closed = True

		for m in Glyphs.font.masters:
			nl = Glyphs.font.glyphs["_pixel"].layers[m.id]
			if len(nl.paths) == 0:
				nl.width = pixSize
				nl.paths.append(newPixel.copy())

		Glyphs.font.userData["PixelPenSetup"] = True
		self.w.close()

	def CancelInitialise(self, sender):
		self.w.close()
		ps = self.w.prevSettings
		Glyphs.font.upm = ps['upm']
		Glyphs.font.grid = ps['gri']
		Glyphs.font.selectedFontMaster.ascender = ps["asc"]
		Glyphs.font.selectedFontMaster.capHeight = ps["cap"]
		Glyphs.font.selectedFontMaster.xHeight = ps["xhe"]
		Glyphs.font.selectedFontMaster.descender = ps["des"]
		Glyphs.font.toolIndex = 0

	def isNumber(self, value):
		try:
			int(value)
			return True
		except:
			return False

	def refreshScreen(self, sender):
		gri = int(self.w.edit_gri.get()) if self.isNumber( self.w.edit_gri.get() ) else 0
		asc = int(self.w.edit_asc.get()) if self.isNumber( self.w.edit_asc.get() ) else 0
		cap = int(self.w.edit_cap.get()) if self.isNumber( self.w.edit_cap.get() ) else 0
		xhe = int(self.w.edit_xhe.get()) if self.isNumber( self.w.edit_xhe.get() ) else 0
		des = int(self.w.edit_des.get()) if self.isNumber( self.w.edit_des.get() ) else 0
		
		upm = (asc - des) * gri
		Glyphs.font.grid = gri
		Glyphs.font.upm = upm
		Glyphs.font.selectedFontMaster.ascender = asc* gri
		Glyphs.font.selectedFontMaster.capHeight = cap* gri
		Glyphs.font.selectedFontMaster.xHeight = xhe* gri
		Glyphs.font.selectedFontMaster.descender = des * gri
		self.w.text_upm.set("UPM will be set to : %s" % upm)
		Glyphs.redraw()