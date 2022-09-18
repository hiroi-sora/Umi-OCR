# http://pmw.sourceforge.net/

import os
import string
import tkinter
# import Pmw
import ui.pmw.PmwBase as Pmw
import collections


class Balloon(Pmw.MegaToplevel):
    def __init__(self, parent=None, **kw):

        # Define the megawidget options.
        optiondefs = (
            ('initwait',                 500,            None),  # milliseconds
            ('label_background',         'lightyellow',  None),
            ('label_foreground',         'black',        None),
            ('label_justify',            'left',         None),
            ('master',                   'parent',       None),
            ('relmouse',                 'none',         self._relmouse),
            ('state',                    'both',         self._state),
            ('statuscommand',            None,           None),
            ('xoffset',                  20,             None),  # pixels
            ('yoffset',                  1,              None),  # pixels
            ('hull_highlightthickness',  1,              None),
            ('hull_highlightbackground', 'black',        None),
        )
        self.defineoptions(kw, optiondefs)

        # Initialise the base class (after defining the options).
        Pmw.MegaToplevel.__init__(self, parent)

        self.withdraw()
        self.overrideredirect(1)

        # Create the components.
        interior = self.interior()
        self._label = self.createcomponent('label',
                                           (), None,
                                           tkinter.Label, (interior,))
        self._label.pack()

        # The default hull configuration options give a black border
        # around the balloon, but avoids a black 'flash' when the
        # balloon is deiconified, before the text appears.
        if 'hull_background' not in kw:
            self.configure(hull_background=str(self._label.cget('background')))

        # Initialise instance variables.
        self._timer = None

        # The widget or item that is currently triggering the balloon.
        # It is None if the balloon is not being displayed.  It is a
        # one-tuple if the balloon is being displayed in response to a
        # widget binding (value is the widget).  It is a two-tuple if
        # the balloon is being displayed in response to a canvas or
        # text item binding (value is the widget and the item).
        self._currentTrigger = None

        # Check keywords and initialise options.
        self.initialiseoptions()

    def destroy(self):
        if self._timer is not None:
            self.after_cancel(self._timer)
            self._timer = None
        Pmw.MegaToplevel.destroy(self)

    def bind(self, widget, balloonHelp, statusHelp=None):

        # If a previous bind for this widget exists, remove it.
        self.unbind(widget)

        if balloonHelp is None and statusHelp is None:
            return

        if statusHelp is None:
            statusHelp = balloonHelp
        enterId = widget.bind('<Enter>',
                              lambda event, self=self, w=widget,
                              sHelp=statusHelp, bHelp=balloonHelp:
                              self._enter(event, w, sHelp, bHelp, 0))

        # Set Motion binding so that if the pointer remains at rest
        # within the widget until the status line removes the help and
        # then the pointer moves again, then redisplay the help in the
        # status line.
        # Note:  The Motion binding only works for basic widgets, and
        # the hull of megawidgets but not for other megawidget components.
        motionId = widget.bind('<Motion>',
                               lambda event=None, self=self, statusHelp=statusHelp:
                               self.showstatus(statusHelp))

        leaveId = widget.bind('<Leave>', self._leave)
        buttonId = widget.bind('<ButtonPress>', self._buttonpress)

        # Set Destroy binding so that the balloon can be withdrawn and
        # the timer can be cancelled if the widget is destroyed.
        destroyId = widget.bind('<Destroy>', self._destroy)

        # Use the None item in the widget's private Pmw dictionary to
        # store the widget's bind callbacks, for later clean up.
        if not hasattr(widget, '_Pmw_BalloonBindIds'):
            widget._Pmw_BalloonBindIds = {}
        widget._Pmw_BalloonBindIds[None] = \
            (enterId, motionId, leaveId, buttonId, destroyId)

    def unbind(self, widget):
        if hasattr(widget, '_Pmw_BalloonBindIds'):
            if None in widget._Pmw_BalloonBindIds:
                (enterId, motionId, leaveId, buttonId, destroyId) = \
                    widget._Pmw_BalloonBindIds[None]
                # Need to pass in old bindings, so that Tkinter can
                # delete the commands.  Otherwise, memory is leaked.
                widget.unbind('<Enter>', enterId)
                widget.unbind('<Motion>', motionId)
                widget.unbind('<Leave>', leaveId)
                widget.unbind('<ButtonPress>', buttonId)
                widget.unbind('<Destroy>', destroyId)
                del widget._Pmw_BalloonBindIds[None]

        if self._currentTrigger is not None and len(self._currentTrigger) == 1:
            # The balloon is currently being displayed and the current
            # trigger is a widget.
            triggerWidget = self._currentTrigger[0]
            if triggerWidget == widget:
                if self._timer is not None:
                    self.after_cancel(self._timer)
                    self._timer = None
                self.withdraw()
                self.clearstatus()
                self._currentTrigger = None

    def tagbind(self, widget, tagOrItem, balloonHelp, statusHelp=None):

        # If a previous bind for this widget's tagOrItem exists, remove it.
        self.tagunbind(widget, tagOrItem)

        if balloonHelp is None and statusHelp is None:
            return

        if statusHelp is None:
            statusHelp = balloonHelp
        enterId = widget.tag_bind(tagOrItem, '<Enter>',
                                  lambda event, self=self, w=widget,
                                  sHelp=statusHelp, bHelp=balloonHelp, tag=tagOrItem:
                                  self._enter(event, w, sHelp, bHelp, 1, tag))
        motionId = widget.tag_bind(tagOrItem, '<Motion>',
                                   lambda event=None, self=self, statusHelp=statusHelp:
                                   self.showstatus(statusHelp))
        leaveId = widget.tag_bind(tagOrItem, '<Leave>', self._leave)
        buttonId = widget.tag_bind(
            tagOrItem, '<ButtonPress>', self._buttonpress)

        # Use the tagOrItem item in the widget's private Pmw dictionary to
        # store the tagOrItem's bind callbacks, for later clean up.
        if not hasattr(widget, '_Pmw_BalloonBindIds'):
            widget._Pmw_BalloonBindIds = {}
        widget._Pmw_BalloonBindIds[tagOrItem] = \
            (enterId, motionId, leaveId, buttonId)

    def tagunbind(self, widget, tagOrItem):
        if hasattr(widget, '_Pmw_BalloonBindIds'):
            if tagOrItem in widget._Pmw_BalloonBindIds:
                (enterId, motionId, leaveId, buttonId) = \
                    widget._Pmw_BalloonBindIds[tagOrItem]
                widget.tag_unbind(tagOrItem, '<Enter>', enterId)
                widget.tag_unbind(tagOrItem, '<Motion>', motionId)
                widget.tag_unbind(tagOrItem, '<Leave>', leaveId)
                widget.tag_unbind(tagOrItem, '<ButtonPress>', buttonId)
                del widget._Pmw_BalloonBindIds[tagOrItem]

        if self._currentTrigger is None:
            # The balloon is not currently being displayed.
            return

        if len(self._currentTrigger) == 1:
            # The current trigger is a widget.
            return

        if len(self._currentTrigger) == 2:
            # The current trigger is a canvas item.
            (triggerWidget, triggerItem) = self._currentTrigger
            if triggerWidget == widget and triggerItem == tagOrItem:
                if self._timer is not None:
                    self.after_cancel(self._timer)
                    self._timer = None
                self.withdraw()
                self.clearstatus()
                self._currentTrigger = None
        else:  # The current trigger is a text item.
            (triggerWidget, x, y) = self._currentTrigger
            if triggerWidget == widget:
                currentPos = widget.index('@%d,%d' % (x, y))
                currentTags = widget.tag_names(currentPos)
                if tagOrItem in currentTags:
                    if self._timer is not None:
                        self.after_cancel(self._timer)
                        self._timer = None
                    self.withdraw()
                    self.clearstatus()
                    self._currentTrigger = None

    def showstatus(self, statusHelp):
        if self['state'] in ('status', 'both'):
            cmd = self['statuscommand']
            if hasattr(cmd, '__call__'):
                cmd(statusHelp)

    def clearstatus(self):
        self.showstatus(None)

    def _state(self):
        if self['state'] not in ('both', 'balloon', 'status', 'none'):
            raise ValueError('bad state option ' + repr(self['state']) +
                             ': should be one of \'both\', \'balloon\', ' +
                             '\'status\' or \'none\'')

    def _relmouse(self):
        if self['relmouse'] not in ('both', 'x', 'y', 'none'):
            raise ValueError('bad relmouse option ' + repr(self['relmouse']) +
                             ': should be one of \'both\', \'x\', ' + '\'y\' or \'none\'')

    def _enter(self, event, widget, statusHelp, balloonHelp, isItem, tagOrItem=None):

        # Do not display balloon if mouse button is pressed.  This
        # will only occur if the button was pressed inside a widget,
        # then the mouse moved out of and then back into the widget,
        # with the button still held down.  The number 0x1f00 is the
        # button mask for the 5 possible buttons in X.
        buttonPressed = (event.state & 0x1f00) != 0

        if not buttonPressed and balloonHelp is not None and \
                self['state'] in ('balloon', 'both'):
            if self._timer is not None:
                self.after_cancel(self._timer)
                self._timer = None

            self._timer = self.after(self['initwait'],
                                     lambda self=self, widget=widget, help=balloonHelp,
                                     isItem=isItem:
                                     self._showBalloon(widget, help, isItem, tagOrItem))

        if isItem:
            if hasattr(widget, 'canvasx'):
                # The widget is a canvas.
                item = widget.find_withtag('current')
                if len(item) > 0:
                    item = item[0]
                else:
                    item = None
                self._currentTrigger = (widget, item)
            else:
                # The widget is a text widget.
                self._currentTrigger = (widget, event.x, event.y)
        else:
            self._currentTrigger = (widget,)

        self.showstatus(statusHelp)

    def _leave(self, event):
        if self._timer is not None:
            self.after_cancel(self._timer)
            self._timer = None
        self.withdraw()
        self.clearstatus()
        self._currentTrigger = None

    def _destroy(self, event):

        # Only withdraw the balloon and cancel the timer if the widget
        # being destroyed is the widget that triggered the balloon.
        # Note that in a Tkinter Destroy event, the widget field is a
        # string and not a widget as usual.

        if self._currentTrigger is None:
            # The balloon is not currently being displayed
            return

        if len(self._currentTrigger) == 1:
            # The current trigger is a widget (not an item)
            triggerWidget = self._currentTrigger[0]
            if str(triggerWidget) == event.widget:
                if self._timer is not None:
                    self.after_cancel(self._timer)
                    self._timer = None
                self.withdraw()
                self.clearstatus()
                self._currentTrigger = None

    def _buttonpress(self, event):
        if self._timer is not None:
            self.after_cancel(self._timer)
            self._timer = None
        self.withdraw()
        self._currentTrigger = None

    def _showBalloon(self, widget, balloonHelp, isItem, tagOrItem=None):

        self._label.configure(text=balloonHelp)

        # First, display the balloon offscreen to get dimensions.
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        self.geometry('+%d+0' % (screenWidth + 1))
        self.update_idletasks()

        if isItem:
            # Get the bounding box of the current item.
            bbox = widget.bbox('current')
            if bbox is None:
                # The item that triggered the balloon has disappeared,
                # perhaps by a user's timer event that occured between
                # the <Enter> event and the 'initwait' timer calling
                # this method.
                return

            # The widget is either a text or canvas.  The meaning of
            # the values returned by the bbox method is different for
            # each, so use the existence of the 'canvasx' method to
            # distinguish between them.
            if hasattr(widget, 'canvasx'):
                # The widget is a canvas.  Place balloon under canvas
                # item.  The positions returned by bbox are relative
                # to the entire canvas, not just the visible part, so
                # need to convert to window coordinates.
                leftrel = bbox[0] - widget.canvasx(0)
                toprel = bbox[1] - widget.canvasy(0)
                bottomrel = bbox[3] - widget.canvasy(0)
            else:
                # The widget is a text widget.  Place balloon under
                # the character closest to the mouse.  The positions
                # returned by bbox are relative to the text widget
                # window (ie the visible part of the text only).
                if tagOrItem is not None:
                    index = widget.index('current')
                    while widget.compare(index, '>', '1.0'):
                        prev_index = widget.index('%s-1c' % index)
                        if tagOrItem in widget.tag_names(prev_index):
                            index = prev_index
                            newbbox = widget.bbox(index)
                            if newbbox == None:
                                break
                            bbox = newbbox
                        else:
                            break
                leftrel = bbox[0]
                toprel = bbox[1]
                bottomrel = bbox[1] + bbox[3]
        else:
            leftrel = 0
            toprel = 0
            bottomrel = widget.winfo_height()

        xpointer, ypointer = widget.winfo_pointerxy()   # -1 if off screen

        if xpointer >= 0 and self['relmouse'] in ('both', 'x'):
            x = xpointer
        else:
            x = leftrel + widget.winfo_rootx()
        x = x + self['xoffset']

        if ypointer >= 0 and self['relmouse'] in ('both', 'y'):
            y = ypointer
        else:
            y = bottomrel + widget.winfo_rooty()
        y = y + self['yoffset']
        edges = (int(str(self.cget('hull_highlightthickness'))) +
                 int(str(self.cget('hull_borderwidth')))) * 2
        if x + self._label.winfo_reqwidth() + edges > screenWidth:
            x = screenWidth - self._label.winfo_reqwidth() - edges

        if y + self._label.winfo_reqheight() + edges > screenHeight:
            if ypointer >= 0 and self['relmouse'] in ('both', 'y'):
                y = ypointer
            else:
                y = toprel + widget.winfo_rooty()
            y = y - self._label.winfo_reqheight() - self['yoffset'] - edges

        Pmw.setgeometryanddeiconify(self, '+%d+%d' % (x, y))
