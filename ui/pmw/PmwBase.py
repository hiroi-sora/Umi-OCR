# http://pmw.sourceforge.net/

# Pmw megawidget base classes.

# This module provides a foundation for building megawidgets.  It
# contains the MegaArchetype class which manages component widgets and
# configuration options.  Also provided are the MegaToplevel and
# MegaWidget classes, derived from the MegaArchetype class.  The
# MegaToplevel class contains a Tkinter Toplevel widget to act as the
# container of the megawidget.  This is used as the base class of all
# megawidgets that are contained in their own top level window, such
# as a Dialog window.  The MegaWidget class contains a Tkinter Frame
# to act as the container of the megawidget.  This is used as the base
# class of all other megawidgets, such as a ComboBox or ButtonBox.
#
# Megawidgets are built by creating a class that inherits from either
# the MegaToplevel or MegaWidget class.

import os
import string
import sys
import traceback
import types
import tkinter
import collections

# tkinter 8.5 -> 8.6 fixed a problem in which selected indexes
# were reported as strings instead of ints
# by default emulate the same functionality so we don't break 
# existing interfaces but allow for easy switching
#_forceTkinter85Compatibility = True

#def setTkinter85Compatible(value):
#    global _forceTkinter85Compatibility
#    if isinstance(value, bool):
#        _forceTkinter85Compatibility = value and tkinter.TkVersion > 8.5
        
#def emulateTk85():
#    global _forceTkinter85Compatibility
#    return _forceTkinter85Compatibility

# Special values used in index() methods of several megawidgets.
END = ['end']
SELECT = ['select']
DEFAULT = ['default']

# Constant used to indicate that an option can only be set by a call
# to the constructor.
INITOPT = ['initopt']
_DEFAULT_OPTION_VALUE = ['default_option_value']
_useTkOptionDb = 0

# Symbolic constants for the indexes into an optionInfo list.
_OPT_DEFAULT         = 0
_OPT_VALUE           = 1
_OPT_FUNCTION        = 2

# Stacks

_busyStack = []
    # Stack which tracks nested calls to show/hidebusycursor (called
    # either directly or from activate()/deactivate()).  Each element
    # is a dictionary containing:
    #   'newBusyWindows' :  List of windows which had busy_hold called
    #                       on them during a call to showbusycursor().
    #                       The corresponding call to hidebusycursor()
    #                       will call busy_release on these windows.
    #   'busyFocus' :       The blt _Busy window which showbusycursor()
    #                       set the focus to.
    #   'previousFocus' :   The focus as it was when showbusycursor()
    #                       was called.  The corresponding call to
    #                       hidebusycursor() will restore this focus if
    #                       the focus has not been changed from busyFocus.

_grabStack = []
    # Stack of grabbed windows.  It tracks calls to push/popgrab()
    # (called either directly or from activate()/deactivate()).  The
    # window on the top of the stack is the window currently with the
    # grab.  Each element is a dictionary containing:
    #   'grabWindow' :      The window grabbed by pushgrab().  The
    #                       corresponding call to popgrab() will release
    #                       the grab on this window and restore the grab
    #                       on the next window in the stack (if there is one).
    #   'globalMode' :      True if the grabWindow was grabbed with a
    #                       global grab, false if the grab was local
    #                       and 'nograb' if no grab was performed.
    #   'previousFocus' :   The focus as it was when pushgrab()
    #                       was called.  The corresponding call to
    #                       popgrab() will restore this focus.
    #   'deactivateFunction' :
    #       The function to call (usually grabWindow.deactivate) if
    #       popgrab() is called (usually from a deactivate() method)
    #       on a window which is not at the top of the stack (that is,
    #       does not have the grab or focus).  For example, if a modal
    #       dialog is deleted by the window manager or deactivated by
    #       a timer.  In this case, all dialogs above and including
    #       this one are deactivated, starting at the top of the
    #       stack.

    # Note that when dealing with focus windows, the name of the Tk
    # widget is used, since it may be the '_Busy' window, which has no
    # python instance associated with it.

#=============================================================================

# Functions used to forward methods from a class to a component.

# Fill in a flattened method resolution dictionary for a class (attributes are
# filtered out). Flattening honours the MI method resolution rules
# (depth-first search of bases in order). The dictionary has method names
# for keys and functions for values.
def __methodDict(cls, dict):

    # the strategy is to traverse the class in the _reverse_ of the normal
    # order, and overwrite any duplicates.
    baseList = list(cls.__bases__)
    baseList.reverse()

    # do bases in reverse order, so first base overrides last base
    for super in baseList:
        __methodDict(super, dict)

    # do my methods last to override base classes
    for key, value in list(cls.__dict__.items()):
        # ignore class attributes
        if type(value) == types.FunctionType:
            dict[key] = value

def __methods(cls):
    # Return all method names for a class.

    # Return all method names for a class (attributes are filtered
    # out).  Base classes are searched recursively.

    dictio = {}
    __methodDict(cls, dictio)
    return list(dictio.keys())

# Function body to resolve a forwarding given the target method name and the
# attribute name. The resulting lambda requires only self, but will forward
# any other parameters.
__stringBody = (
    'def %(method)s(this, *args, **kw): return ' +
    #'apply(this.%(attribute)s.%(method)s, args, kw)')
    'this.%(attribute)s.%(method)s(*args, **kw)');

# Get a unique id
__counter = 0
def __unique():
    global __counter
    __counter = __counter + 1
    return str(__counter)

# Function body to resolve a forwarding given the target method name and the
# index of the resolution function. The resulting lambda requires only self,
# but will forward any other parameters. The target instance is identified
# by invoking the resolution function.
__funcBody = (
    'def %(method)s(this, *args, **kw): return ' +
    #'apply(this.%(forwardFunc)s().%(method)s, args, kw)')
    'this.%(forwardFunc)s().%(method)s(*args, **kw)');

def forwardmethods(fromClass, toClass, toPart, exclude = ()):
    # Forward all methods from one class to another.

    # Forwarders will be created in fromClass to forward method
    # invocations to toClass.  The methods to be forwarded are
    # identified by flattening the interface of toClass, and excluding
    # methods identified in the exclude list.  Methods already defined
    # in fromClass, or special methods with one or more leading or
    # trailing underscores will not be forwarded.

    # For a given object of class fromClass, the corresponding toClass
    # object is identified using toPart.  This can either be a String
    # denoting an attribute of fromClass objects, or a function taking
    # a fromClass object and returning a toClass object.

    # Example:
    #     class MyClass:
    #     ...
    #         def __init__(self):
    #             ...
    #             self.__target = TargetClass()
    #             ...
    #         def findtarget(self):
    #             return self.__target
    #     forwardmethods(MyClass, TargetClass, '__target', ['dangerous1', 'dangerous2'])
    #     # ...or...
    #     forwardmethods(MyClass, TargetClass, MyClass.findtarget,
    #             ['dangerous1', 'dangerous2'])

    # In both cases, all TargetClass methods will be forwarded from
    # MyClass except for dangerous1, dangerous2, special methods like
    # __str__, and pre-existing methods like findtarget.


    # Allow an attribute name (String) or a function to determine the instance
    if not isinstance(toPart, str):

        # check that it is something like a function
        if hasattr(toPart, '__call__'):

            # If a method is passed, use the function within it
            if hasattr(toPart, 'im_func'):
                toPart = toPart.__func__

            # After this is set up, forwarders in this class will use
            # the forwarding function. The forwarding function name is
            # guaranteed to be unique, so that it can't be hidden by subclasses
            forwardName = '__fwdfunc__' + __unique()
            fromClass.__dict__[forwardName] = toPart

        # It's not a valid type
        else:
            raise TypeError('toPart must be attribute name, function or method')

    # get the full set of candidate methods
    dict = {}
    __methodDict(toClass, dict)

    # discard special methods
    for ex in list(dict.keys()):
        if ex[:1] == '_' or ex[-1:] == '_':
            del dict[ex]
    # discard dangerous methods supplied by the caller
    for ex in exclude:
        if ex in dict:
            del dict[ex]
    # discard methods already defined in fromClass
    for ex in __methods(fromClass):
        if ex in dict:
            del dict[ex]

    for method, func in list(dict.items()):
        d = {'method': method, 'func': func}
        if isinstance(toPart, str):
            execString = \
                __stringBody % {'method' : method, 'attribute' : toPart}
        else:
            execString = \
                __funcBody % {'forwardFunc' : forwardName, 'method' : method}

        exec(execString, d)

        # this creates a method
        #fromClass.__dict__[method] = d[method]
        setattr(fromClass, method, d[method])


#=============================================================================

def setgeometryanddeiconify(window, geom):
    # To avoid flashes on X and to position the window correctly on NT
    # (caused by Tk bugs).

    if os.name == 'nt' or \
            (os.name == 'posix' and sys.platform[:6] == 'cygwin'):
        # Require overrideredirect trick to stop window frame
        # appearing momentarily.
        redirect = window.overrideredirect()
        if not redirect:
            window.overrideredirect(1)
        window.deiconify()
        if geom is not None:
            window.geometry(geom)
        # Call update_idletasks to ensure NT moves the window to the
        # correct position it is raised.
        window.update_idletasks()
        window.tkraise()
        if not redirect:
            window.overrideredirect(0)
    else:
        if geom is not None:
            window.geometry(geom)

        # Problem!?  Which way around should the following two calls
        # go?  If deiconify() is called first then I get complaints
        # from people using the enlightenment or sawfish window
        # managers that when a dialog is activated it takes about 2
        # seconds for the contents of the window to appear.  But if
        # tkraise() is called first then I get complaints from people
        # using the twm window manager that when a dialog is activated
        # it appears in the top right corner of the screen and also
        # takes about 2 seconds to appear.

        #window.tkraise()
        # Call update_idletasks to ensure certain window managers (eg:
        # enlightenment and sawfish) do not cause Tk to delay for
        # about two seconds before displaying window.
        #window.update_idletasks()
        #window.deiconify()

        window.deiconify()
        if window.overrideredirect():
            # The window is not under the control of the window manager
            # and so we need to raise it ourselves.
            window.tkraise()

#=============================================================================

class MegaArchetype:
    # Megawidget abstract root class.

    # This class provides methods which are inherited by classes
    # implementing useful bases (this class doesn't provide a
    # container widget inside which the megawidget can be built).

    def __init__(self, parent = None, hullClass = None):

        # Mapping from each megawidget option to a list of information
        # about the option
        #   - default value
        #   - current value
        #   - function to call when the option is initialised in the
        #     call to initialiseoptions() in the constructor or
        #     modified via configure().  If this is INITOPT, the
        #     option is an initialisation option (an option that can
        #     be set by the call to the constructor but can not be
        #     used with configure).
        # This mapping is not initialised here, but in the call to
        # defineoptions() which precedes construction of this base class.
        #
        # self._optionInfo = {}

        # Mapping from each component name to a tuple of information
        # about the component.
        #   - component widget instance
        #   - configure function of widget instance
        #   - the class of the widget (Frame, EntryField, etc)
        #   - cget function of widget instance
        #   - the name of the component group of this component, if any
        self.__componentInfo = {}

        # Mapping from alias names to the names of components or
        # sub-components.
        self.__componentAliases = {}

        # Contains information about the keywords provided to the
        # constructor.  It is a mapping from the keyword to a tuple
        # containing:
        #    - value of keyword
        #    - a boolean indicating if the keyword has been used.
        # A keyword is used if, during the construction of a megawidget,
        #    - it is defined in a call to defineoptions() or addoptions(), or
        #    - it references, by name, a component of the megawidget, or
        #    - it references, by group, at least one component
        # At the end of megawidget construction, a call is made to
        # initialiseoptions() which reports an error if there are
        # unused options given to the constructor.
        #
        # After megawidget construction, the dictionary contains
        # keywords which refer to a dynamic component group, so that
        # these components can be created after megawidget
        # construction and still use the group options given to the
        # constructor.
        #
        # self._constructorKeywords = {}

        # List of dynamic component groups.  If a group is included in
        # this list, then it not an error if a keyword argument for
        # the group is given to the constructor or to configure(), but
        # no components with this group have been created.
        # self._dynamicGroups = ()

        if hullClass is None:
            self._hull = None
        else:
            if parent is None:
                parent = tkinter._default_root

            # Create the hull.
            self._hull = self.createcomponent('hull',
                    (), None,
                    hullClass, (parent,))
            _hullToMegaWidget[self._hull] = self

            if _useTkOptionDb:
                # Now that a widget has been created, query the Tk
                # option database to get the default values for the
                # options which have not been set in the call to the
                # constructor.  This assumes that defineoptions() is
                # called before the __init__().
                option_get = self.option_get
                _VALUE = _OPT_VALUE
                _DEFAULT = _OPT_DEFAULT
                for name, info in list(self._optionInfo.items()):
                    value = info[_VALUE]
                    if value is _DEFAULT_OPTION_VALUE:
                        resourceClass = str.upper(name[0]) + name[1:]
                        value = option_get(name, resourceClass)
                        if value != '':
                            try:
                                # Convert the string to int/float/tuple, etc
                                value = eval(value, {'__builtins__': {}})
                            except:
                                pass
                            info[_VALUE] = value
                        else:
                            info[_VALUE] = info[_DEFAULT]

    def destroy(self):
        # Clean up optionInfo in case it contains circular references
        # in the function field, such as self._settitle in class
        # MegaToplevel.

        self._optionInfo = {}
        if self._hull is not None:
            del _hullToMegaWidget[self._hull]
            self._hull.destroy()

    #======================================================================
    # Methods used (mainly) during the construction of the megawidget.

    def defineoptions(self, keywords, optionDefs, dynamicGroups = ()):
        # Create options, providing the default value and the method
        # to call when the value is changed.  If any option created by
        # base classes has the same name as one in <optionDefs>, the
        # base class's value and function will be overriden.

        # This should be called before the constructor of the base
        # class, so that default values defined in the derived class
        # override those in the base class.

        if not hasattr(self, '_constructorKeywords'):
            # First time defineoptions has been called.
            tmp = {}
            for option, value in list(keywords.items()):
                tmp[option] = [value, 0]
            self._constructorKeywords = tmp
            self._optionInfo = {}
            self._initialiseoptions_counter = 0
        self._initialiseoptions_counter = self._initialiseoptions_counter + 1

        if not hasattr(self, '_dynamicGroups'):
            self._dynamicGroups = ()
        self._dynamicGroups = self._dynamicGroups + tuple(dynamicGroups)
        self.addoptions(optionDefs)

    def addoptions(self, optionDefs):
        # Add additional options, providing the default value and the
        # method to call when the value is changed.  See
        # "defineoptions" for more details

        # optimisations:
        optionInfo = self._optionInfo
        #optionInfo_has_key = optionInfo.has_key
        keywords = self._constructorKeywords
        #keywords_has_key = keywords.has_key
        FUNCTION = _OPT_FUNCTION

        for name, default, function in optionDefs:
            if '_' not in name:
                # The option will already exist if it has been defined
                # in a derived class.  In this case, do not override the
                # default value of the option or the callback function
                # if it is not None.
                if not name in optionInfo:
                    if name in keywords:
                        value = keywords[name][0]
                        optionInfo[name] = [default, value, function]
                        del keywords[name]
                    else:
                        if _useTkOptionDb:
                            optionInfo[name] = \
                                    [default, _DEFAULT_OPTION_VALUE, function]
                        else:
                            optionInfo[name] = [default, default, function]
                elif optionInfo[name][FUNCTION] is None:
                    optionInfo[name][FUNCTION] = function
            else:
                # This option is of the form "component_option".  If this is
                # not already defined in self._constructorKeywords add it.
                # This allows a derived class to override the default value
                # of an option of a component of a base class.
                if not name in keywords:
                    keywords[name] = [default, 0]

    def createcomponent(self, componentName, componentAliases,
            componentGroup, widgetClass, *widgetArgs, **kw):
        #print('inCreateComponent', componentName)
        # Create a component (during construction or later).

        if componentName in self.__componentInfo:
            raise ValueError('Component "%s" already exists' % componentName)

        if '_' in componentName:
            raise ValueError('Component name "%s" must not contain "_"' % componentName)

        if hasattr(self, '_constructorKeywords'):
            keywords = self._constructorKeywords
        else:
            keywords = {}
        for alias, component in componentAliases:
            # Create aliases to the component and its sub-components.
            index = str.find(component, '_')
            if index < 0:
                self.__componentAliases[alias] = (component, None)
            else:
                mainComponent = component[:index]
                subComponent = component[(index + 1):]
                self.__componentAliases[alias] = (mainComponent, subComponent)

            # Remove aliases from the constructor keyword arguments by
            # replacing any keyword arguments that begin with *alias*
            # with corresponding keys beginning with *component*.

            alias = alias + '_'
            aliasLen = len(alias)
            for option in list(keywords.keys()):
                if len(option) > aliasLen and option[:aliasLen] == alias:
                    newkey = component + '_' + option[aliasLen:]
                    keywords[newkey] = keywords[option]
                    del keywords[option]

        componentPrefix = componentName + '_'
        nameLen = len(componentPrefix)
        for option in list(keywords.keys()):
            if len(option) > nameLen and option[:nameLen] == componentPrefix:
                # The keyword argument refers to this component, so add
                # this to the options to use when constructing the widget.
                kw[option[nameLen:]] = keywords[option][0]
                del keywords[option]
            else:
                # Check if this keyword argument refers to the group
                # of this component.  If so, add this to the options
                # to use when constructing the widget.  Mark the
                # keyword argument as being used, but do not remove it
                # since it may be required when creating another
                # component.
                index = str.find(option, '_')
                if index >= 0 and componentGroup == option[:index]:
                    rest = option[(index + 1):]
                    kw[rest] = keywords[option][0]
                    keywords[option][1] = 1

        if 'pyclass' in kw:
            widgetClass = kw['pyclass']
            del kw['pyclass']
        if widgetClass is None:
            return None
        if len(widgetArgs) == 1 and type(widgetArgs[0]) == tuple:
            # Arguments to the constructor can be specified as either
            # multiple trailing arguments to createcomponent() or as a
            # single tuple argument.
            widgetArgs = widgetArgs[0]
        widget = widgetClass(*widgetArgs, **kw)
        componentClass = widget.__class__.__name__
        self.__componentInfo[componentName] = (widget, widget.configure,
                componentClass, widget.cget, componentGroup)

        return widget

    def destroycomponent(self, name):
        # Remove a megawidget component.

        # This command is for use by megawidget designers to destroy a
        # megawidget component.

        self.__componentInfo[name][0].destroy()
        del self.__componentInfo[name]

    def createlabel(self, parent, childCols = 1, childRows = 1):

        labelpos = self['labelpos']
        labelmargin = self['labelmargin']
        if labelpos is None:
            return

        label = self.createcomponent('label',
                (), None,
                tkinter.Label, (parent,))

        if labelpos[0] in 'ns':
            # vertical layout
            if labelpos[0] == 'n':
                row = 0
                margin = 1
            else:
                row = childRows + 3
                margin = row - 1
            label.grid(column=2, row=row, columnspan=childCols, sticky=labelpos)
            parent.grid_rowconfigure(margin, minsize=labelmargin)
        else:
            # horizontal layout
            if labelpos[0] == 'w':
                col = 0
                margin = 1
            else:
                col = childCols + 3
                margin = col - 1
            label.grid(column=col, row=2, rowspan=childRows, sticky=labelpos)
            parent.grid_columnconfigure(margin, minsize=labelmargin)

    def initialiseoptions(self, dummy = None):
        self._initialiseoptions_counter = self._initialiseoptions_counter - 1
        if self._initialiseoptions_counter == 0:
            unusedOptions = []
            keywords = self._constructorKeywords
            for name in list(keywords.keys()):
                used = keywords[name][1]
                if not used:
                    # This keyword argument has not been used.  If it
                    # does not refer to a dynamic group, mark it as
                    # unused.
                    index = str.find(name, '_')
                    if index < 0 or name[:index] not in self._dynamicGroups:
                        unusedOptions.append(name)
            if len(unusedOptions) > 0:
                if len(unusedOptions) == 1:
                    text = 'Unknown option "'
                else:
                    text = 'Unknown options "'
                raise KeyError(text + str.join(unusedOptions, ', ') + \
                        '" for ' + self.__class__.__name__)

            # Call the configuration callback function for every option.
            FUNCTION = _OPT_FUNCTION
            for info in list(self._optionInfo.values()):
                func = info[FUNCTION]
                if func is not None and func is not INITOPT:
                    func()

    #======================================================================
    # Method used to configure the megawidget.

    def configure(self, option=None, **kw):
        # Query or configure the megawidget options.
        #
        # If not empty, *kw* is a dictionary giving new
        # values for some of the options of this megawidget or its
        # components.  For options defined for this megawidget, set
        # the value of the option to the new value and call the
        # configuration callback function, if any.  For options of the
        # form <component>_<option>, where <component> is a component
        # of this megawidget, call the configure method of the
        # component giving it the new value of the option.  The
        # <component> part may be an alias or a component group name.
        #
        # If *option* is None, return all megawidget configuration
        # options and settings.  Options are returned as standard 5
        # element tuples.
        #
        # If *option* is a string, return the 5 element tuple for the
        # given configuration option.

        # First, deal with the option queries.
        if len(kw) == 0:
            # This configure call is querying the values of one or all options.
            # Return 5-tuples:
            #     (optionName, resourceName, resourceClass, default, value)
            if option is None:
                rtn = {}
                for option, config in list(self._optionInfo.items()):
                    resourceClass = str.upper(option[0]) + option[1:]
                    rtn[option] = (option, option, resourceClass,
                            config[_OPT_DEFAULT], config[_OPT_VALUE])
                return rtn
            else:
                config = self._optionInfo[option]
                resourceClass = str.upper(option[0]) + option[1:]
                return (option, option, resourceClass, config[_OPT_DEFAULT],
                        config[_OPT_VALUE])

        # optimisations:
        optionInfo = self._optionInfo
        componentInfo = self.__componentInfo
        componentAliases = self.__componentAliases
        VALUE = _OPT_VALUE
        FUNCTION = _OPT_FUNCTION

        # This will contain a list of options in *kw* which
        # are known to this megawidget.
        directOptions = []

        # This will contain information about the options in
        # *kw* of the form <component>_<option>, where
        # <component> is a component of this megawidget.  It is a
        # dictionary whose keys are the configure method of each
        # component and whose values are a dictionary of options and
        # values for the component.
        indirectOptions = {}

        for option, value in list(kw.items()):
            if option in optionInfo:
                # This is one of the options of this megawidget.
                # Make sure it is not an initialisation option.
                if optionInfo[option][FUNCTION] is INITOPT:
                    raise KeyError(
                            'Cannot configure initialisation option "'
                            + option + '" for ' + self.__class__.__name__)
                optionInfo[option][VALUE] = value
                directOptions.append(option)
            else:
                index = option.find('_')
                if index >= 0:
                    # This option may be of the form <component>_<option>.
                    component = option[:index]
                    componentOption = option[(index + 1):]

                    # Expand component alias
                    if component in componentAliases:
                        component, subComponent = componentAliases[component]
                        if subComponent is not None:
                            componentOption = subComponent + '_' \
                                    + componentOption

                        # Expand option string to write on error
                        option = component + '_' + componentOption

                    if component in componentInfo:
                        # Configure the named component
                        componentConfigFuncs = [componentInfo[component][1]]
                    else:
                        # Check if this is a group name and configure all
                        # components in the group.
                        componentConfigFuncs = []
                        for info in list(componentInfo.values()):
                            if info[4] == component:
                                componentConfigFuncs.append(info[1])

                        if len(componentConfigFuncs) == 0 and \
                                component not in self._dynamicGroups:
                            raise KeyError('Unknown option "' + option +
                                    '" for ' + self.__class__.__name__)

                    # Add the configure method(s) (may be more than
                    # one if this is configuring a component group)
                    # and option/value to dictionary.
                    for componentConfigFunc in componentConfigFuncs:
                        if not componentConfigFunc in indirectOptions:
                            indirectOptions[componentConfigFunc] = {}
                        indirectOptions[componentConfigFunc][componentOption] \
                                = value
                else:
                    raise KeyError('Unknown option "' + option +
                            '" for ' + self.__class__.__name__)

        # Call the configure methods for any components.
        for func, values in indirectOptions.items():
            func(**values);

        # Call the configuration callback function for each option.
        for option in directOptions:
            info = optionInfo[option]
            func = info[_OPT_FUNCTION]
            if func is not None:
                func()

    def __setitem__(self, key, value):
        self.configure(**{key: value})

    #======================================================================
    # Methods used to query the megawidget.

    def component(self, name):
        # Return a component widget of the megawidget given the
        # component's name
        # This allows the user of a megawidget to access and configure
        # widget components directly.

        # Find the main component and any subcomponents
        index = str.find(name, '_')
        if index < 0:
            component = name
            remainingComponents = None
        else:
            component = name[:index]
            remainingComponents = name[(index + 1):]

        # Expand component alias
        if component in self.__componentAliases:
            component, subComponent = self.__componentAliases[component]
            if subComponent is not None:
                if remainingComponents is None:
                    remainingComponents = subComponent
                else:
                    remainingComponents = subComponent + '_' \
                            + remainingComponents

        widget = self.__componentInfo[component][0]
        if remainingComponents is None:
            return widget
        else:
            return widget.component(remainingComponents)

    def interior(self):
        return self._hull

    def hulldestroyed(self):
        return self._hull not in _hullToMegaWidget

    def __str__(self):
        return str(self._hull)

    def cget(self, option):
        # Get current configuration setting.

        # Return the value of an option, for example myWidget['font'].
        if option in self._optionInfo:
            return self._optionInfo[option][_OPT_VALUE]
        else:
            index = str.find(option, '_')
            if index >= 0:
                component = option[:index]
                componentOption = option[(index + 1):]

                # Expand component alias
                if component in self.__componentAliases:
                    component, subComponent = self.__componentAliases[component]
                    if subComponent is not None:
                        componentOption = subComponent + '_' + componentOption

                    # Expand option string to write on error
                    option = component + '_' + componentOption

                if component in self.__componentInfo:
                    # Call cget on the component.
                    componentCget = self.__componentInfo[component][3]
                    return componentCget(componentOption)
                else:
                    # If this is a group name, call cget for one of
                    # the components in the group.
                    for info in list(self.__componentInfo.values()):
                        if info[4] == component:
                            componentCget = info[3]
                            return componentCget(componentOption)

        raise KeyError('Unknown option "' + option + \
                '" for ' + self.__class__.__name__)

    __getitem__ = cget

    def isinitoption(self, option):
        return self._optionInfo[option][_OPT_FUNCTION] is INITOPT

    def options(self):
        options = []
        if hasattr(self, '_optionInfo'):
            for option, info in list(self._optionInfo.items()):
                isinit = info[_OPT_FUNCTION] is INITOPT
                default = info[_OPT_DEFAULT]
                options.append((option, default, isinit))
            options.sort()
        return options

    def components(self):
        # Return a list of all components.

        # This list includes the 'hull' component and all widget subcomponents

        names = list(self.__componentInfo.keys())
        names.sort()
        return names

    def componentaliases(self):
        # Return a list of all component aliases.

        componentAliases = self.__componentAliases

        names = list(componentAliases.keys())
        names.sort()
        rtn = []
        for alias in names:
            (mainComponent, subComponent) = componentAliases[alias]
            if subComponent is None:
                rtn.append((alias, mainComponent))
            else:
                rtn.append((alias, mainComponent + '_' + subComponent))

        return rtn

    def componentgroup(self, name):
        return self.__componentInfo[name][4]

#=============================================================================

# The grab functions are mainly called by the activate() and
# deactivate() methods.
#
# Use pushgrab() to add a new window to the grab stack.  This
# releases the grab by the window currently on top of the stack (if
# there is one) and gives the grab and focus to the new widget.
#
# To remove the grab from the window on top of the grab stack, call
# popgrab().
#
# Use releasegrabs() to release the grab and clear the grab stack.

def pushgrab(grabWindow, globalMode, deactivateFunction):
    prevFocus = grabWindow.tk.call('focus')
    grabInfo = {
        'grabWindow' : grabWindow,
        'globalMode' : globalMode,
        'previousFocus' : prevFocus,
        'deactivateFunction' : deactivateFunction,
    }
    _grabStack.append(grabInfo)
    _grabtop()
    grabWindow.focus_set()

def popgrab(window):
    # Return the grab to the next window in the grab stack, if any.

    # If this window is not at the top of the grab stack, then it has
    # just been deleted by the window manager or deactivated by a
    # timer.  Call the deactivate method for the modal dialog above
    # this one on the stack.
    if _grabStack[-1]['grabWindow'] != window:
        for index in range(len(_grabStack)):
            if _grabStack[index]['grabWindow'] == window:
                _grabStack[index + 1]['deactivateFunction']()
                break

    grabInfo = _grabStack[-1]
    del _grabStack[-1]

    topWidget = grabInfo['grabWindow']
    prevFocus = grabInfo['previousFocus']
    globalMode = grabInfo['globalMode']

    if globalMode != 'nograb':
        topWidget.grab_release()

    if len(_grabStack) > 0:
        _grabtop()
    if prevFocus != '':
        try:
            topWidget.tk.call('focus', prevFocus)
        except tkinter.TclError:
            # Previous focus widget has been deleted. Set focus
            # to root window.
            tkinter._default_root.focus_set()
    else:
        # Make sure that focus does not remain on the released widget.
        if len(_grabStack) > 0:
            topWidget = _grabStack[-1]['grabWindow']
            topWidget.focus_set()
        else:
            tkinter._default_root.focus_set()

def grabstacktopwindow():
    if len(_grabStack) == 0:
        return None
    else:
        return _grabStack[-1]['grabWindow']

def releasegrabs():
    # Release grab and clear the grab stack.

    current = tkinter._default_root.grab_current()
    if current is not None:
        current.grab_release()
    _grabStack[:] = []

def _grabtop():
    grabInfo = _grabStack[-1]
    topWidget = grabInfo['grabWindow']
    globalMode = grabInfo['globalMode']

    if globalMode == 'nograb':
        return

    while 1:
        try:
            if globalMode:
                topWidget.grab_set_global()
            else:
                topWidget.grab_set()
            break
        except tkinter.TclError:
            # Another application has grab.  Keep trying until
            # grab can succeed.
            topWidget.after(100)

#=============================================================================

class MegaToplevel(MegaArchetype):

    def __init__(self, parent = None, **kw):
        # Define the options for this megawidget.
        optiondefs = (
            ('activatecommand',   None,                     None),
            ('deactivatecommand', None,                     None),
            ('master',            None,                     None),
            ('title',             None,                     self._settitle),
            ('hull_class',        self.__class__.__name__,  None),
        )
        self.defineoptions(kw, optiondefs)

        # Initialise the base class (after defining the options).
        super().__init__(parent, tkinter.Toplevel)
        
        # Initialise instance.

        # Set WM_DELETE_WINDOW protocol, deleting any old callback, so
        # memory does not leak.
        if hasattr(self._hull, '_Pmw_WM_DELETE_name'):
            self._hull.tk.deletecommand(self._hull._Pmw_WM_DELETE_name)
        self._hull._Pmw_WM_DELETE_name = \
                self.register(self._userdeletewindow, needcleanup = 0)
        self.protocol('WM_DELETE_WINDOW', self._hull._Pmw_WM_DELETE_name)

        # Initialise instance variables.

        self._firstShowing = 1
        # Used by show() to ensure window retains previous position on screen.

        # The IntVar() variable to wait on during a modal dialog.
        self._wait = None

        self._active = 0
        self._userdeletefunc = self.destroy
        self._usermodaldeletefunc = self.deactivate

        # Check keywords and initialise options.
        self.initialiseoptions()

    def _settitle(self):
        title = self['title']
        if title is not None:
            self.title(title)

    def userdeletefunc(self, func=None):
        if func:
            self._userdeletefunc = func
        else:
            return self._userdeletefunc

    def usermodaldeletefunc(self, func=None):
        if func:
            self._usermodaldeletefunc = func
        else:
            return self._usermodaldeletefunc

    def _userdeletewindow(self):
        if self.active():
            self._usermodaldeletefunc()
        else:
            self._userdeletefunc()

    def destroy(self):
        # Allow this to be called more than once.
        if self._hull in _hullToMegaWidget:
            self.deactivate()

            # Remove circular references, so that object can get cleaned up.
            del self._userdeletefunc
            del self._usermodaldeletefunc

            MegaArchetype.destroy(self)

    def show(self, master = None):
        if self.state() != 'normal':
            if self._firstShowing:
                # Just let the window manager determine the window
                # position for the first time.
                geom = None
            else:
                # Position the window at the same place it was last time.
                geom = self._sameposition()
            setgeometryanddeiconify(self, geom)

        if self._firstShowing:
            self._firstShowing = 0
        else:
            if self.transient() == '':
                self.tkraise()

        # Do this last, otherwise get flashing on NT:
        if master is not None:
            if master == 'parent':
                parent = self.winfo_parent()
                # winfo_parent() should return the parent widget, but the
                # the current version of Tkinter returns a string.
                if type(parent) is str:
                    parent = self._hull._nametowidget(parent)
                master = parent.winfo_toplevel()
            self.transient(master)

        self.focus()

    def _centreonscreen(self):
        # Centre the window on the screen.  (Actually halfway across
        # and one third down.)

        parent = self.winfo_parent()
        if type(parent) is str:
            parent = self._hull._nametowidget(parent)

        # Find size of window.
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        if width == 1 and height == 1:
            # If the window has not yet been displayed, its size is
            # reported as 1x1, so use requested size.
            width = self.winfo_reqwidth()
            height = self.winfo_reqheight()

        # Place in centre of screen:
        x = (self.winfo_screenwidth() - width) / 2 - parent.winfo_vrootx()
        y = (self.winfo_screenheight() - height) / 3 - parent.winfo_vrooty()
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        return '+%d+%d' % (x, y)

    def _sameposition(self):
        # Position the window at the same place it was last time.

        geometry = self.geometry()
        index = str.find(geometry, '+')
        if index >= 0:
            return geometry[index:]
        else:
            return None

    def activate(self, globalMode = 0, geometry = 'centerscreenfirst'):
        if self._active:
            raise ValueError('Window is already active')
        if self.state() == 'normal':
            self.withdraw()

        self._active = 1

        showbusycursor()

        if self._wait is None:
            self._wait = tkinter.IntVar()
        self._wait.set(0)

        if geometry == 'centerscreenalways':
            geom = self._centreonscreen()
        elif geometry == 'centerscreenfirst':
            if self._firstShowing:
                # Centre the window the first time it is displayed.
                geom = self._centreonscreen()
            else:
                # Position the window at the same place it was last time.
                geom = self._sameposition()
        elif geometry[:5] == 'first':
            if self._firstShowing:
                geom = geometry[5:]
            else:
                # Position the window at the same place it was last time.
                geom = self._sameposition()
        else:
            geom = geometry

        self._firstShowing = 0

        setgeometryanddeiconify(self, geom)

        # Do this last, otherwise get flashing on NT:
        master = self['master']
        if master is not None:
            if master == 'parent':
                parent = self.winfo_parent()
                # winfo_parent() should return the parent widget, but the
                # the current version of Tkinter returns a string.
                if type(parent) is str:
                    parent = self._hull._nametowidget(parent)
                master = parent.winfo_toplevel()
            self.transient(master)

        pushgrab(self._hull, globalMode, self.deactivate)
        command = self['activatecommand']
        if hasattr(command, '__call__'):
            command()
        self.wait_variable(self._wait)

        return self._result

    def deactivate(self, result=None):
        if not self._active:
            return
        self._active = 0

        # Restore the focus before withdrawing the window, since
        # otherwise the window manager may take the focus away so we
        # can't redirect it.  Also, return the grab to the next active
        # window in the stack, if any.
        popgrab(self._hull)

        command = self['deactivatecommand']
        if hasattr(command, '__call__'):
            command()

        self.withdraw()
        hidebusycursor(forceFocusRestore = 1)

        self._result = result
        self._wait.set(1)

    def active(self):
        return self._active

forwardmethods(MegaToplevel, tkinter.Toplevel, '_hull')

#=============================================================================

class MegaWidget(MegaArchetype):
    def __init__(self, parent = None, **kw):
        # Define the options for this megawidget.
        optiondefs = (
            ('hull_class',       self.__class__.__name__,  None),
        )
        self.defineoptions(kw, optiondefs)

        # Initialise the base class (after defining the options).
        MegaArchetype.__init__(self, parent, tkinter.Frame)

        # Check keywords and initialise options.
        self.initialiseoptions()

forwardmethods(MegaWidget, tkinter.Frame, '_hull')

#=============================================================================

# Public functions
#-----------------

_traceTk = 0
def tracetk(root = None, on = 1, withStackTrace = 0, file=None):
    global _withStackTrace
    global _traceTkFile
    global _traceTk

    if root is None:
        root = tkinter._default_root
    
    _withStackTrace = withStackTrace
    _traceTk = on
    if on == 1:
        # This causes trace not to work - not enabled by default in tk anymore?
        # if hasattr(root.tk, '__class__'):
        #   # Tracing already on
        #    return
        if file is None:
            _traceTkFile = sys.stderr
        else:
            _traceTkFile = file
        tk = _TraceTk(root.tk)
    else:
        if not hasattr(root.tk, '__class__'):
            # Tracing already off
            return
        tk = root.tk.getTclInterp()
    _setTkInterps(root, tk)

def showbusycursor():

    _addRootToToplevelBusyInfo()
    root = tkinter._default_root

    busyInfo = {
        'newBusyWindows' : [],
        'previousFocus' : None,
        'busyFocus' : None,
    }
    _busyStack.append(busyInfo)

    if _disableKeyboardWhileBusy:
        # Remember the focus as it is now, before it is changed.
        busyInfo['previousFocus'] = root.tk.call('focus')

    if not _havebltbusy(root):
        # No busy command, so don't call busy hold on any windows.
        return

    for (window, winInfo) in list(_toplevelBusyInfo.items()):
        if (window.state() != 'withdrawn' and not winInfo['isBusy']
                and not winInfo['excludeFromBusy']):
            busyInfo['newBusyWindows'].append(window)
            winInfo['isBusy'] = 1
            _busy_hold(window, winInfo['busyCursorName'])

            # Make sure that no events for the busy window get
            # through to Tkinter, otherwise it will crash in
            # _nametowidget with a 'KeyError: _Busy' if there is
            # a binding on the toplevel window.
            window.tk.call('bindtags', winInfo['busyWindow'], 'Pmw_Dummy_Tag')

            if _disableKeyboardWhileBusy:
                # Remember previous focus widget for this toplevel window
                # and set focus to the busy window, which will ignore all
                # keyboard events.
                winInfo['windowFocus'] = \
                        window.tk.call('focus', '-lastfor', window._w)
                window.tk.call('focus', winInfo['busyWindow'])
                busyInfo['busyFocus'] = winInfo['busyWindow']

    if len(busyInfo['newBusyWindows']) > 0:
        if os.name == 'nt':
            # NT needs an "update" before it will change the cursor.
            window.update()
        else:
            window.update_idletasks()

def hidebusycursor(forceFocusRestore = 0):

    # Remember the focus as it is now, before it is changed.
    root = tkinter._default_root
    if _disableKeyboardWhileBusy:
        currentFocus = root.tk.call('focus')

    # Pop the busy info off the stack.
    busyInfo = _busyStack[-1]
    del _busyStack[-1]

    for window in busyInfo['newBusyWindows']:
        # If this window has not been deleted, release the busy cursor.
        if window in _toplevelBusyInfo:
            winInfo = _toplevelBusyInfo[window]
            winInfo['isBusy'] = 0
            _busy_release(window)

            if _disableKeyboardWhileBusy:
                # Restore previous focus window for this toplevel window,
                # but only if is still set to the busy window (it may have
                # been changed).
                windowFocusNow = window.tk.call('focus', '-lastfor', window._w)
                if windowFocusNow == winInfo['busyWindow']:
                    try:
                        window.tk.call('focus', winInfo['windowFocus'])
                    except tkinter.TclError:
                        # Previous focus widget has been deleted. Set focus
                        # to toplevel window instead (can't leave focus on
                        # busy window).
                        window.focus_set()

    if _disableKeyboardWhileBusy:
        # Restore the focus, depending on whether the focus had changed
        # between the calls to showbusycursor and hidebusycursor.
        if forceFocusRestore or busyInfo['busyFocus'] == currentFocus:
            # The focus had not changed, so restore it to as it was before
            # the call to showbusycursor,
            previousFocus = busyInfo['previousFocus']
            if previousFocus is not None:
                try:
                    root.tk.call('focus', previousFocus)
                except tkinter.TclError:
                    # Previous focus widget has been deleted; forget it.
                    pass
        else:
            # The focus had changed, so restore it to what it had been
            # changed to before the call to hidebusycursor.
            root.tk.call('focus', currentFocus)

def clearbusycursor():
    while len(_busyStack) > 0:
        hidebusycursor()

def setbusycursorattributes(window, **kw):
    _addRootToToplevelBusyInfo()
    for name, value in list(kw.items()):
        if name == 'exclude':
            _toplevelBusyInfo[window]['excludeFromBusy'] = value
        elif name == 'cursorName':
            _toplevelBusyInfo[window]['busyCursorName'] = value
        else:
            raise KeyError('Unknown busycursor attribute "' + name + '"')

def _addRootToToplevelBusyInfo():
    # Include the Tk root window in the list of toplevels.  This must
    # not be called before Tkinter has had a chance to be initialised by
    # the application.

    root = tkinter._default_root
    if root == None:
        root = tkinter.Tk()
    if root not in _toplevelBusyInfo:
        _addToplevelBusyInfo(root)

def busycallback(command, updateFunction = None):
    if not hasattr(command, '__call__'):
        raise ValueError('cannot register non-command busy callback %s %s' % \
                (repr(command), type(command)))
    wrapper = _BusyWrapper(command, updateFunction)
    return wrapper.callback

_errorReportFile = None
_errorWindow = None

def reporterrorstofile(file = None):
    global _errorReportFile
    _errorReportFile = file

def displayerror(text):
    global _errorWindow

    if _errorReportFile is not None:
        _errorReportFile.write(text + '\n')
    else:
        # Print error on standard error as well as to error window.
        # Useful if error window fails to be displayed, for example
        # when exception is triggered in a <Destroy> binding for root
        # window.
        sys.stderr.write(text + '\n')

        if _errorWindow is None:
            # The error window has not yet been created.
            _errorWindow = _ErrorWindow()

        _errorWindow.showerror(text)

_root = None
_disableKeyboardWhileBusy = 1

def initialise(
        root = None,
        size = None,
        fontScheme = None,
        useTkOptionDb = 0,
        noBltBusy = 0,
        disableKeyboardWhileBusy = None,
):
    # Remember if show/hidebusycursor should ignore keyboard events.
    global _disableKeyboardWhileBusy
    if disableKeyboardWhileBusy is not None:
        _disableKeyboardWhileBusy = disableKeyboardWhileBusy

    # Do not use blt busy command if noBltBusy is set.  Otherwise,
    # use blt busy if it is available.
    global _haveBltBusy
    if noBltBusy:
        _haveBltBusy = 0

    # Save flag specifying whether the Tk option database should be
    # queried when setting megawidget option default values.
    global _useTkOptionDb
    _useTkOptionDb = useTkOptionDb

    # If we haven't been given a root window, use the default or
    # create one.
    if root is None:
        if tkinter._default_root is None:
            root = tkinter.Tk()
        else:
            root = tkinter._default_root

    # If this call is initialising a different Tk interpreter than the
    # last call, then re-initialise all global variables.  Assume the
    # last interpreter has been destroyed - ie:  Pmw does not (yet)
    # support multiple simultaneous interpreters.
    global _root
    if _root is not None and _root != root:
        global _busyStack
        global _errorWindow
        global _grabStack
        global _hullToMegaWidget
        global _toplevelBusyInfo
        _busyStack = []
        _errorWindow = None
        _grabStack = []
        _hullToMegaWidget = {}
        _toplevelBusyInfo = {}
    _root = root

    # Trap Tkinter Toplevel constructors so that a list of Toplevels
    # can be maintained.
    tkinter.Toplevel.title = __TkinterToplevelTitle

    # Trap Tkinter widget destruction so that megawidgets can be
    # destroyed when their hull widget is destoyed and the list of
    # Toplevels can be pruned.
    tkinter.Toplevel.destroy = __TkinterToplevelDestroy
    tkinter.Widget.destroy = __TkinterWidgetDestroy

    # Modify Tkinter's CallWrapper class to improve the display of
    # errors which occur in callbacks.
    tkinter.CallWrapper = __TkinterCallWrapper

    # Make sure we get to know when the window manager deletes the
    # root window.  Only do this if the protocol has not yet been set.
    # This is required if there is a modal dialog displayed and the
    # window manager deletes the root window.  Otherwise the
    # application will not exit, even though there are no windows.
    if root.protocol('WM_DELETE_WINDOW') == '':
        root.protocol('WM_DELETE_WINDOW', root.destroy)

    # Set the base font size for the application and set the
    # Tk option database font resources.
    from . import PmwLogicalFont
    PmwLogicalFont._font_initialise(root, size, fontScheme)
    return root

def alignlabels(widgets, sticky = None):
    if len(widgets) == 0:
        return

    widgets[0].update_idletasks()

    # Determine the size of the maximum length label string.
    maxLabelWidth = 0
    for iwid in widgets:
        labelWidth = iwid.grid_bbox(0, 1)[2]
        if labelWidth > maxLabelWidth:
            maxLabelWidth = labelWidth

    # Adjust the margins for the labels such that the child sites and
    # labels line up.
    for iwid in widgets:
        if sticky is not None:
            iwid.component('label').grid(sticky=sticky)
        iwid.grid_columnconfigure(0, minsize = maxLabelWidth)
#=============================================================================

# Private routines
#-----------------
_callToTkReturned = 1
_recursionCounter = 1

class _TraceTk:
    def __init__(self, tclInterp):
        self.tclInterp = tclInterp

    def getTclInterp(self):
        return self.tclInterp

    # Calling from python into Tk.
    def call(self, *args, **kw):
        global _callToTkReturned
        global _recursionCounter

        _callToTkReturned = 0
        if len(args) == 1 and type(args[0]) == tuple:
            argStr = str(args[0])
        else:
            argStr = str(args)
        _traceTkFile.write('CALL  TK> %d:%s%s' %
                (_recursionCounter, '  ' * _recursionCounter, argStr))
        _recursionCounter = _recursionCounter + 1
        try:
            result = self.tclInterp.call(*args, **kw)
        except tkinter.TclError as errorString:
            _callToTkReturned = 1
            _recursionCounter = _recursionCounter - 1
            _traceTkFile.write('\nTK ERROR> %d:%s-> %s\n' %
                    (_recursionCounter, '  ' * _recursionCounter,
                            repr(errorString)))
            if _withStackTrace:
                _traceTkFile.write('CALL  TK> stack:\n')
                traceback.print_stack()
            raise tkinter.TclError(errorString)

        _recursionCounter = _recursionCounter - 1
        if _callToTkReturned:
            _traceTkFile.write('CALL RTN> %d:%s-> %s' %
                    (_recursionCounter, '  ' * _recursionCounter, repr(result)))
        else:
            _callToTkReturned = 1
            if result:
                _traceTkFile.write(' -> %s' % repr(result))
        _traceTkFile.write('\n')
        if _withStackTrace:
            _traceTkFile.write('CALL  TK> stack:\n')
            traceback.print_stack()

        _traceTkFile.flush()
        return result

    def __getattr__(self, key):
        return getattr(self.tclInterp, key)

def _setTkInterps(window, tk):
    window.tk = tk
    for child in list(window.children.values()):
        _setTkInterps(child, tk)

#=============================================================================

# Functions to display a busy cursor.  Keep a list of all toplevels
# and display the busy cursor over them.  The list will contain the Tk
# root toplevel window as well as all other toplevel windows.
# Also keep a list of the widget which last had focus for each
# toplevel.

# Map from toplevel windows to
#     {'isBusy', 'windowFocus', 'busyWindow',
#         'excludeFromBusy', 'busyCursorName'}
_toplevelBusyInfo = {}

# Pmw needs to know all toplevel windows, so that it can call blt busy
# on them.  This is a hack so we get notified when a Tk topevel is
# created.  Ideally, the __init__ 'method' should be overridden, but
# it is a 'read-only special attribute'.  Luckily, title() is always
# called from the Tkinter Toplevel constructor.

def _addToplevelBusyInfo(window):
    if window._w == '.':
        busyWindow = '._Busy'
    else:
        busyWindow = window._w + '._Busy'

    _toplevelBusyInfo[window] = {
        'isBusy' : 0,
        'windowFocus' : None,
        'busyWindow' : busyWindow,
        'excludeFromBusy' : 0,
        'busyCursorName' : None,
    }

def __TkinterToplevelTitle(self, *args):
    # If this is being called from the constructor, include this
    # Toplevel in the list of toplevels and set the initial
    # WM_DELETE_WINDOW protocol to destroy() so that we get to know
    # about it.
    if self not in _toplevelBusyInfo:
        _addToplevelBusyInfo(self)
        self._Pmw_WM_DELETE_name = self.register(self.destroy, None, 0)
        self.protocol('WM_DELETE_WINDOW', self._Pmw_WM_DELETE_name)

    return tkinter.Wm.title(*(self,) + args)

_haveBltBusy = None
def _havebltbusy(window):
    global _busy_hold, _busy_release, _haveBltBusy
    if _haveBltBusy is None:
        from . import PmwBlt
        _haveBltBusy = PmwBlt.havebltbusy(window)
        _busy_hold = PmwBlt.busy_hold
        if os.name == 'nt':
            # There is a bug in Blt 2.4i on NT where the busy window
            # does not follow changes in the children of a window.
            # Using forget works around the problem.
            _busy_release = PmwBlt.busy_forget
        else:
            _busy_release = PmwBlt.busy_release
    return _haveBltBusy

class _BusyWrapper:
    def __init__(self, command, updateFunction):
        self._command = command
        self._updateFunction = updateFunction

    def callback(self, *args):
        showbusycursor()
        rtn = self._command(*args)

        # Call update before hiding the busy windows to clear any
        # events that may have occurred over the busy windows.
        if hasattr(self._updateFunction, '__call__'):
            self._updateFunction()

        hidebusycursor()
        return rtn

#=============================================================================

def drawarrow(canvas, color, direction, tag, baseOffset = 0.25, edgeOffset = 0.15):
    canvas.delete(tag)

    bw = (int(canvas['borderwidth']) +
            int(canvas['highlightthickness']))
    width = int(canvas['width'])
    height = int(canvas['height'])

    if direction in ('up', 'down'):
        majorDimension = height
        minorDimension = width
    else:
        majorDimension = width
        minorDimension = height

    offset = round(baseOffset * majorDimension)
    if direction in ('down', 'right'):
        base = bw + offset
        apex = bw + majorDimension - offset
    else:
        base = bw + majorDimension - offset
        apex = bw + offset

    if minorDimension > 3 and minorDimension % 2 == 0:
        minorDimension = minorDimension - 1
    half = int(minorDimension * (1 - 2 * edgeOffset)) / 2
    low = round(bw + edgeOffset * minorDimension)
    middle = low + half
    high = low + 2 * half

    if direction in ('up', 'down'):
        coords = (low, base, high, base, middle, apex)
    else:
        coords = (base, low, base, high, apex, middle)
    kw = {'fill' : color, 'outline' : color, 'tag' : tag}
    canvas.create_polygon(*coords, **kw)

#=============================================================================

# Modify the Tkinter destroy methods so that it notifies us when a Tk
# toplevel or frame is destroyed.

# A map from the 'hull' component of a megawidget to the megawidget.
# This is used to clean up a megawidget when its hull is destroyed.
_hullToMegaWidget = {}

def __TkinterToplevelDestroy(tkWidget):
    if tkWidget in _hullToMegaWidget:
        mega = _hullToMegaWidget[tkWidget]
        try:
            mega.destroy()
        except:
            _reporterror(mega.destroy, ())
    else:
        # Delete the busy info structure for this toplevel (if the
        # window was created before Pmw.initialise() was called, it
        # will not have any.
        if tkWidget in _toplevelBusyInfo:
            del _toplevelBusyInfo[tkWidget]
        if hasattr(tkWidget, '_Pmw_WM_DELETE_name'):
            tkWidget.tk.deletecommand(tkWidget._Pmw_WM_DELETE_name)
            del tkWidget._Pmw_WM_DELETE_name
        tkinter.BaseWidget.destroy(tkWidget)

def __TkinterWidgetDestroy(tkWidget):
    if tkWidget in _hullToMegaWidget:
        mega = _hullToMegaWidget[tkWidget]
        try:
            mega.destroy()
        except:
            _reporterror(mega.destroy, ())
    else:
        tkinter.BaseWidget.destroy(tkWidget)

#=============================================================================

# Add code to Tkinter to improve the display of errors which occur in
# callbacks.

class __TkinterCallWrapper:
    def __init__(self, func, subst, widget):
        self.func = func
        self.subst = subst
        self.widget = widget

    # Calling back from Tk into python.
    def __call__(self, *args):
        try:
            if self.subst:
                args = self.subst(*args)
            if _traceTk:
                if not _callToTkReturned:
                    _traceTkFile.write('\n')
                if hasattr(self.func, 'im_class'):
                    name = self.func.__self__.__class__.__name__ + '.' + \
                        self.func.__name__
                else:
                    name = self.func.__name__
                if len(args) == 1 and hasattr(args[0], 'type'):
                    # The argument to the callback is an event.
                    eventName = _eventTypeToName[int(args[0].type)]
                    if eventName in ('KeyPress', 'KeyRelease',):
                        argStr = '(%s %s Event: %s)' % \
                            (eventName, args[0].keysym, args[0].widget)
                    else:
                        argStr = '(%s Event, %s)' % (eventName, args[0].widget)
                else:
                    argStr = str(args)
                _traceTkFile.write('CALLBACK> %d:%s%s%s\n' %
                    (_recursionCounter, '  ' * _recursionCounter, name, argStr))
                _traceTkFile.flush()
            return self.func(*args)
        except SystemExit as msg:
            raise SystemExit(msg)
        except:
            _reporterror(self.func, args)

_eventTypeToName = {
    2 : 'KeyPress',         15 : 'VisibilityNotify',   28 : 'PropertyNotify',
    3 : 'KeyRelease',       16 : 'CreateNotify',       29 : 'SelectionClear',
    4 : 'ButtonPress',      17 : 'DestroyNotify',      30 : 'SelectionRequest',
    5 : 'ButtonRelease',    18 : 'UnmapNotify',        31 : 'SelectionNotify',
    6 : 'MotionNotify',     19 : 'MapNotify',          32 : 'ColormapNotify',
    7 : 'EnterNotify',      20 : 'MapRequest',         33 : 'ClientMessage',
    8 : 'LeaveNotify',      21 : 'ReparentNotify',     34 : 'MappingNotify',
    9 : 'FocusIn',          22 : 'ConfigureNotify',    35 : 'VirtualEvents',
    10 : 'FocusOut',        23 : 'ConfigureRequest',   36 : 'ActivateNotify',
    11 : 'KeymapNotify',    24 : 'GravityNotify',      37 : 'DeactivateNotify',
    12 : 'Expose',          25 : 'ResizeRequest',      38 : 'MouseWheelEvent',
    13 : 'GraphicsExpose',  26 : 'CirculateNotify',
    14 : 'NoExpose',        27 : 'CirculateRequest',
}

def _reporterror(func, args):
    # Fetch current exception values.
    exc_type, exc_value, exc_traceback = sys.exc_info()

    # Give basic information about the callback exception.
    if type(exc_type) == type:
        # Handle python 1.5 class exceptions.
        exc_type = exc_type.__name__
    msg = str(exc_type) + ' Exception in Tk callback\n'
    msg = msg + '  Function: %s (type: %s)\n' % (repr(func), type(func))
    msg = msg + '  Args: %s\n' % str(args)

    if type(args) == tuple and len(args) > 0 and \
            hasattr(args[0], 'type'):
        eventArg = 1
    else:
        eventArg = 0

    # If the argument to the callback is an event, add the event type.
    if eventArg:
        eventNum = int(args[0].type)
        if eventNum in list(_eventTypeToName.keys()):
            msg = msg + '  Event type: %s (type num: %d)\n' % \
                    (_eventTypeToName[eventNum], eventNum)
        else:
            msg = msg + '  Unknown event type (type num: %d)\n' % eventNum

    # Add the traceback.
    msg = msg + 'Traceback (innermost last):\n'
    for tr in traceback.extract_tb(exc_traceback):
        msg = msg + '  File "%s", line %s, in %s\n' % (tr[0], tr[1], tr[2])
        msg = msg + '    %s\n' % tr[3]
    msg = msg + '%s: %s\n' % (exc_type, exc_value)

    # If the argument to the callback is an event, add the event contents.
    if eventArg:
        msg = msg + '\n================================================\n'
        msg = msg + '  Event contents:\n'
        keys = list(args[0].__dict__.keys())
        keys.sort()
        for key in keys:
            msg = msg + '    %s: %s\n' % (key, args[0].__dict__[key])

    clearbusycursor()
    try:
        displayerror(msg)
    except:
        pass

class _ErrorWindow:
    def __init__(self):

        self._errorQueue = []
        self._errorCount = 0
        self._open = 0
        self._firstShowing = 1

        # Create the toplevel window
        self._top = tkinter.Toplevel()
        self._top.protocol('WM_DELETE_WINDOW', self._hide)
        self._top.title('Error in background function')
        self._top.iconname('Background error')

        # Create the text widget and scrollbar in a frame
        upperframe = tkinter.Frame(self._top)

        scrollbar = tkinter.Scrollbar(upperframe, orient='vertical')
        scrollbar.pack(side = 'right', fill = 'y')

        self._text = tkinter.Text(upperframe, yscrollcommand=scrollbar.set)
        self._text.pack(fill = 'both', expand = 1)
        scrollbar.configure(command=self._text.yview)

        # Create the buttons and label in a frame
        lowerframe = tkinter.Frame(self._top)

        ignore = tkinter.Button(lowerframe,
                text = 'Ignore remaining errors', command = self._hide)
        ignore.pack(side='left')

        self._nextError = tkinter.Button(lowerframe,
                text = 'Show next error', command = self._next)
        self._nextError.pack(side='left')

        self._label = tkinter.Label(lowerframe, relief='ridge')
        self._label.pack(side='left', fill='x', expand=1)

        # Pack the lower frame first so that it does not disappear
        # when the window is resized.
        lowerframe.pack(side = 'bottom', fill = 'x')
        upperframe.pack(side = 'bottom', fill = 'both', expand = 1)

    def showerror(self, text):
        if self._open:
            self._errorQueue.append(text)
        else:
            self._display(text)
            self._open = 1

        # Display the error window in the same place it was before.
        if self._top.state() == 'normal':
            # If update_idletasks is not called here, the window may
            # be placed partially off the screen.  Also, if it is not
            # called and many errors are generated quickly in
            # succession, the error window may not display errors
            # until the last one is generated and the interpreter
            # becomes idle.
            # XXX: remove this, since it causes omppython to go into an
            # infinite loop if an error occurs in an omp callback.
            # self._top.update_idletasks()

            pass
        else:
            if self._firstShowing:
                geom = None
            else:
                geometry = self._top.geometry()
                index = str.find(geometry, '+')
                if index >= 0:
                    geom = geometry[index:]
                else:
                    geom = None
            setgeometryanddeiconify(self._top, geom)

        if self._firstShowing:
            self._firstShowing = 0
        else:
            self._top.tkraise()

        self._top.focus()

        self._updateButtons()

        # Release any grab, so that buttons in the error window work.
        releasegrabs()

    def _hide(self):
        self._errorCount = self._errorCount + len(self._errorQueue)
        self._errorQueue = []
        self._top.withdraw()
        self._open = 0

    def _next(self):
        # Display the next error in the queue.

        text = self._errorQueue[0]
        del self._errorQueue[0]

        self._display(text)
        self._updateButtons()

    def _display(self, text):
        self._errorCount = self._errorCount + 1
        text = 'Error: %d\n%s' % (self._errorCount, text)
        self._text.delete('1.0', 'end')
        self._text.insert('end', text)

    def _updateButtons(self):
        numQueued = len(self._errorQueue)
        if numQueued > 0:
            self._label.configure(text='%d more errors' % numQueued)
            self._nextError.configure(state='normal')
        else:
            self._label.configure(text='No more errors')
            self._nextError.configure(state='disabled')
