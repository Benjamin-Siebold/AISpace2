from ipywidgets import DOMWidget, register
from traitlets import Dict, Unicode, observe

from .cspjsonbridge import csp_from_json, csp_to_json, csp_to_python_code
import json

@register('aispace.CSPBuilder')
class CSPBuilder(DOMWidget):
    """A Jupyter widget that allows for visual creation of a CSP."""
    _view_name = Unicode('CSPBuilder').tag(sync=True)
    _model_name = Unicode('CSPBuilderModel').tag(sync=True)
    _view_module = Unicode('aispace').tag(sync=True)
    _model_module = Unicode('aispace').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)
    graph_json = Dict().tag(sync=True)

    def __init__(self, csp=None):
        super().__init__()
        (self.graph_json, _, _) = csp_to_json(csp)

    @observe('graph_json')
    def _observe_graph_json(self, _):
        self.send({'action': 'python-code', 'code': json.dumps(self.graph_json)})

    def csp(self):
        """Converts the CSP represented by this builder into a Python CSP object."""
        return csp_from_json(self.graph_json)

    def py_code(self):
        """Converts the CSP represented by this builder into Python code."""

        self.send({'action': 'request-python-code'})
