import math

import pytest

from ipytone.base import NativeAudioNode, NativeAudioParam
from ipytone.core import Destination, Gain, InternalAudioNode, Param, get_destination


def test_internal_audio_node():
    node = InternalAudioNode(type="test")

    assert node.number_of_inputs == 1
    assert node.number_of_outputs == 1
    assert repr(node) == "InternalAudioNode(type='test')"


def test_param():
    param = Param()

    assert param.value == 1
    assert param.units == "number"
    assert param.convert is True
    assert param.min_value == -math.inf
    assert param.max_value == math.inf
    assert param.overridden is False
    assert repr(param) == "Param(value=1.0, units='number')"
    assert isinstance(param.input, NativeAudioParam)

    param2 = Param(min_value=-0.2, max_value=0.2, swappable=True)

    assert param2.min_value == -0.2
    assert param2.max_value == 0.2
    assert isinstance(param2.input, NativeAudioNode)


@pytest.mark.parametrize(
    "units,expected_range",
    [
        ("audio_range", (-1, 1)),
        ("normal_range", (0, 1)),
        ("time", (0, math.inf)),
        ("decibels", (-math.inf, math.inf)),
    ],
)
def test_param_min_max_value(units, expected_range):
    param = Param(units=units)
    actual_range = (param.min_value, param.max_value)
    assert actual_range == expected_range


def test_gain():
    gain = Gain()

    assert gain.gain.value == 1
    assert gain.gain.units == "gain"
    assert isinstance(gain.input, NativeAudioNode)
    assert gain.input is gain.output
    assert repr(gain) == "Gain(gain=Param(value=1.0, units='gain'))"

    s = gain.dispose()
    assert s is gain
    assert gain.disposed is True
    assert gain.gain.disposed is True


def test_destination():
    dest = get_destination()

    assert dest.mute is False
    assert dest.volume == -16
    assert isinstance(dest.input, InternalAudioNode)
    assert isinstance(dest.output, Gain)

    # test singleton
    dest1 = Destination()
    dest2 = Destination()

    assert dest1 == dest2 == get_destination()