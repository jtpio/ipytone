from ipywidgets import Widget, widget_serialization
from traitlets import Instance, Int, List, Unicode

from ._frontend import module_name, module_version


class ToneWidgetBase(Widget):
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)


class AudioNode(ToneWidgetBase):
    """An audio node widget."""

    _model_name = Unicode("AudioNodeModel").tag(sync=True)

    name = Unicode("").tag(sync=True)

    _in_nodes = List(Instance(Widget)).tag(sync=True, **widget_serialization)
    _out_nodes = List(Instance(Widget)).tag(sync=True, **widget_serialization)

    number_of_inputs = Int(
        read_only=True,
        default_value=1,
        help="The number of inputs feeding into the AudioNode"
    ).tag(sync=True)

    number_of_outputs = Int(
        read_only=True,
        default_value=1,
        help="The number of outputs of the AudioNode"
    ).tag(sync=True)

    def _normalize_destination(self, destination):
        if isinstance(destination, AudioNode):
            destination = [destination]

        if not all([isinstance(d, AudioNode) for d in destination]):
            raise ValueError("destination(s) must be AudioNode object(s)")
        if any([not d.number_of_inputs for d in destination]):
            raise ValueError("cannot connect to source audio node(s)")
        if self in destination:
            raise ValueError("cannot connect an audio node to itself")

        return list(set(self._out_nodes) | set(destination))

    def connect(self, destination):
        """Connect the output of this audio node to another ``destination`` audio node."""

        if destination not in self._out_nodes:
            self._out_nodes = self._normalize_destination(destination)
            destination._in_nodes = destination._in_nodes + [self]

        return self

    def disconnect(self, destination):
        """Disconnect the ouput of this audio node from a connected destination."""

        new_out_nodes = list(self._out_nodes)
        new_out_nodes.remove(destination)
        self._out_nodes = new_out_nodes

        new_in_nodes = list(destination._in_nodes)
        new_in_nodes.remove(self)
        destination._in_nodes = new_in_nodes

        return self

    def fan(self, *destinations):
        """Connect the output of this audio node to the ``destinations`` audio nodes in parallel."""

        self._out_nodes = self._normalize_destination(destinations)

        for node in destinations:
            node._in_nodes = node._in_nodes + [self]

        return self

    def chain(self, *nodes):
        """Connect the output of this audio node to the other audio nodes in series."""

        chain_nodes = [self] + list(nodes)

        for i in range(len(chain_nodes) - 1):
            chain_nodes[i].connect(chain_nodes[i + 1])

        return self

    def to_destination(self):
        """Convenience method to directly connect the output of this audio node
        to the master node.

        """
        from .core import get_destination

        self.connect(get_destination())

        return self

    @property
    def output(self):
        """Get all audio nodes connected to the output of this node."""
        return list(self._out_nodes)

    @property
    def input(self):
        """Get all audio nodes connected to the input of this node."""
        return list(self._in_nodes)

    def _repr_keys(self):
        if self.name:
            yield "name"
