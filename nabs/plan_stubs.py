"""
Plan pieces that may be useful for assembling plans.

This is the LCLS counterpart to `bluesky.plan_stubs`.

The plans in this module are not meant to be run individually, instead these
are intended as building blocks for other complete plans.
"""
import logging

from bluesky.plan_stubs import subscribe
from bluesky.plans import count
from bluesky.preprocessors import stub_wrapper

from nabs.streams import AverageStream

logger = logging.getLogger(__name__)


def measure_average(detectors, num, delay=None, stream=None):
    """
    Measure an average over a number of shots from a set of detectors.

    Parameters
    ----------
    detectors : list
        List of detectors to read

    num : int
        Number of shots to average together

    delay : iterable or scalar, optional
        Time delay between successive readings. See `bluesky.plans.count`
        for more details

    stream : `nabs.streams.AverageStream`, optional
        If a plan will call `measure_average` multiple times, a single
        ``AverageStream`` instance can be created and then passed in on each
        call. This allows other callbacks to subscribe to the averaged data
        stream. If no ``AverageStream`` is provided then one is created for the
        purpose of this function.

    Returns
    -------
    averaged_event : dict
        A dictionary of all the measurements taken from the list of detectors
        averaged for ``num`` shots. The keys follow the same naming convention
        as that will appear in the event documents i.e "{name}_{field}"

    Notes
    -----
    The returned average dictionary will only contain keys for 'number' or
    'array' fields. Field types that can not be averaged such as 'string' will
    be ignored, do not expect them in the output.
    """
    # Create a stream and subscribe if not given one
    if not stream:
        stream = AverageStream(num=num)
        yield from subscribe('all', stream)
        # Manually kick the LiveDispatcher to emit a start document because we
        # will not see the original one since this is subscribed after open_run
        stream.start({'uid': None})
    # Ensure we sync our stream with request if using a prior one
    else:
        stream.num = num
    # Measure our detectors
    yield from stub_wrapper(count(detectors, num=num, delay=delay))
    # Return the measured average as a dictionary for use in adaptive plans
    return stream.last_event
