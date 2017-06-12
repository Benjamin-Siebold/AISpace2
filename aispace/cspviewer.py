import importlib
import multiprocessing
import threading
from functools import partial
from time import sleep

import ipywidgets as widgets
from IPython.display import display
from ipywidgets import CallbackDispatcher, DOMWidget, Output, register
from traitlets import Integer, Unicode, observe

from aipython.utilities import Displayable, cspToJson

@register('aispace.CSPViewer')
class CSPViewer(DOMWidget):
    """Visualize and interact with a CSP."""
    _view_name = Unicode('HelloView').tag(sync=True)
    _model_name = Unicode('HelloModel').tag(sync=True)
    _view_module = Unicode('aispace').tag(sync=True)
    _model_module = Unicode('aispace').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)
    
    # value = Unicode('Hello World!!!!').tag(sync=True)
    jsonRepr = Unicode('{}').tag(sync=True)
    # process_id = Integer(0).tag(sync=True)

    def __init__(self, csp):
        super(CSPViewer, self).__init__()
        self.on_msg(self._handle_custom_msgs)
        self.jsonRepr = cspToJson(csp)
        self._desired_level = 4
        self.sleep_time = 0.2

        # If Con_solver is not defined at the time of creation, import the existing one
        try:
            module = importlib.import_module('__main__')
            Con_solver = getattr(module, 'Con_solver')
        except AttributeError:
            module = importlib.import_module('aipython.cspConsistency')
            Con_solver = getattr(module, 'Con_solver')

        self._con_solver = Con_solver(csp)
        self._con_solver.display = self.display
        self._block_for_user_input = threading.Event()

        def arc_select(to_do):
            if self._desired_level == 1:
                return to_do.pop()

            self._block_for_user_input.wait()
            
            if self._user_selected_arc:
                to_do.discard(self._selected_arc)
                return self._selected_arc
            else:
                # User did not select. Return random arc
                return to_do.pop()

        self._con_solver.wait_for_arc_selection = arc_select

        def bootstrap():
            # self.process_id = threading.current_thread().ident
            self._con_solver.make_arc_consistent()

        self.thread = threading.Thread(target=bootstrap)
        self.thread.start()

        self._selected_arc = None
        self._user_selected_arc = False

        """yield example
        self.gen = self.con_solver.make_arc_consistent()
        self.to_dos = next(self.gen)
        self.a = widgets.Button(description='DANGER!')
        self.a.on_click(lambda _: self.gen.send(self.to_dos.pop()))

        display(self.a)
        """

        def step(btn):
            self._user_selected_arc = False
            self._desired_level = 2
            self._block_for_user_input.set()
            self._block_for_user_input.clear()

        def fine_step(btn):
            self._user_selected_arc = False
            self._desired_level = 4
            self._block_for_user_input.set()
            self._block_for_user_input.clear()

        def auto_arc(btn):
            self._user_selected_arc = False
            self._desired_level = 1
            self._block_for_user_input.set()
            self._block_for_user_input.clear()

        fine_step_btn = widgets.Button(description='Fine Step')
        fine_step_btn.on_click(fine_step)
        step_btn = widgets.Button(description='Step')
        step_btn.on_click(step)
        auto_arc_btn = widgets.Button(description='Auto Arc Consistency')
        auto_arc_btn.on_click(auto_arc)
        reset_btn = widgets.Button(description='Reset')
        
        display(widgets.HBox([fine_step_btn, step_btn, auto_arc_btn]))

    def _handle_custom_msgs(self, _, content, buffers=None):
        if content.get('event', '') == 'constraint:click':
            varChar = content.get('varId')
            const = self._con_solver.csp.constraints[content.get('constId')]
            self._desired_level = 2
            # Search through to_do to find the one to pop
            '''if (varChar, const) in self.to_dos:
                print("FOUND!")
                self.to_dos.discard((varChar, const))
                try:
                    self.to_dos = self.gen.send((varChar, const))
                except StopIteration:
                    pass'''

            self._selected_arc = (varChar, const)
            self._user_selected_arc = True
            self._block_for_user_input.set()
            self._block_for_user_input.clear()
    
    def display(self, level, *args, **kwargs):
        """print the arguments if level is less than or equal to the
        current max_display_level.
        level is an integer.
        the other arguments are whatever arguments print can take.
        """
        shouldWait = True
        if args[0] == 'Domain pruned':
            nodeName = args[2]
            consName = args[6]
            for key, value in kwargs.items():
                elementValues = value
                for elementValue in elementValues:
                    self.send({'action': 'reduceDomain', 'nodeName': nodeName,
                        'elementValue': elementValue})
                   # reduceDomain(nodeName, elementValue)

        if args[0] == "Processing arc (":
            varName = args[1]
            consName = args[3]
            self.send({'action': 'highlightArc', 'varName': varName,
                'consName': consName.__repr__(), 'style': 'bold',
                'colour': 'na'})
            for i in range(len(self._con_solver.csp.constraints)):
                if self._con_solver.csp.constraints[i] == consName:
                    self.send({'action': 'highlightArc', 'varName': varName,
                'consName': consName.__repr__(), 'style': 'bold',
                'colour': 'na'})
            # highlightArc(varName, consName.__repr__(), "bold","na")
            
        if args[0] == 'Domain pruned':
            varName = args[2]
            consName = args[6]
            self.send({'action': 'highlightArc', 'varName': varName,
                'consName': consName.__repr__(), 'style': 'bold',
                'colour': 'green'})
            # highlightArc(varName, consName.__repr__(), "bold","green")
            
        if args[0] == "Arc: (" and args[4] == ") is inconsistent":
            varName = args[1]
            consName = args[3]
            self.send({'action': 'highlightArc', 'varName': varName,
                'consName': consName.__repr__(), 'style': 'bold',
                'colour': 'red'})
            # highlightArc(varName, consName.__repr__(), "bold","red")
            
        if args[0] == "Arc: (" and args[4] == ") now consistent":
            varName = args[1]
            consName = args[3]
            self.send({'action': 'highlightArc', 'varName': varName,
                'consName': consName.__repr__(), 'style': '!bold',
                'colour': 'green'})
            shouldWait = False
            # highlightArc(varName, consName.__repr__(), "!bold","green")
        
        if args[0] == "  adding" and args[2] == "to to_do.":
            if args[1] != "nothing":
                arcList = list(args[1])
                for i in range(len(arcList)):
                    self.send({'action': 'highlightArc', 'varName': arcList[i][0],
                'consName': arcList[i][1].__repr__(), 'style': '!bold',
                'colour': 'blue'})

        text = ' '.join(map(str, args))
        self.send({'action': 'output', 'result': text})

        if level <= self._desired_level:
            if shouldWait:
                self._block_for_user_input.wait()
        else:
            sleep(self.sleep_time)