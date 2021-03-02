import pytest

from ipytone.base import NativeAudioNode, NativeAudioParam
from ipytone.core import InternalAudioNode, Param


@pytest.mark.parametrize(
    "src,dest,param",
    [
        (InternalAudioNode(), InternalAudioNode(), Param()),
        (NativeAudioNode(), NativeAudioNode(), NativeAudioParam()),
    ],
)
def test_audio_graph(audio_graph, src, dest, param):
    with audio_graph.hold_state():
        audio_graph.connect(src, dest)
        assert (src, dest) not in audio_graph.connections
    assert (src, dest) in audio_graph.connections

    audio_graph.connect(src, param)
    assert (src, param) in audio_graph.connections

    assert audio_graph.nodes == list({src, dest, param})
    assert audio_graph.connections == [(src, dest), (src, param)]

    with audio_graph.hold_state():
        audio_graph.disconnect(src, dest)
        assert (src, dest) in audio_graph.connections
    assert (src, dest) not in audio_graph.connections


def test_audio_graph_errors(audio_graph):
    src = InternalAudioNode()
    dest = InternalAudioNode()
    param = Param()

    with pytest.raises(ValueError, match=".*not connected to.*"):
        audio_graph.disconnect(src, dest)

    with pytest.raises(ValueError, match="src_node must be.*"):
        audio_graph.connect(param, dest)

    with pytest.raises(ValueError, match=".*dest_node must be.*"):
        audio_graph.connect(src, "not a node")

    src = InternalAudioNode()
    dest = InternalAudioNode(_n_inputs=0)
    with pytest.raises(ValueError, match="Cannot connect to audio source.*"):
        audio_graph.connect(src, dest)

    src = InternalAudioNode(_n_outputs=0)
    dest = InternalAudioNode()
    with pytest.raises(ValueError, match="Cannot connect from audio sink.*"):
        audio_graph.connect(src, dest)