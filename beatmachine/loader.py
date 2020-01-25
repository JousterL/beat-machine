"""
The ``loader`` module contains functions for loading beats from song files.
"""
from typing import BinaryIO, Union, Generator, Callable, Iterable, Tuple

import numpy as np
from madmom.audio import Signal

BeatLoader = Callable[[Union[str, BinaryIO]], Tuple[int, Iterable[np.ndarray]]]


def load_beats_by_signal(
    fp: Union[str, BinaryIO], min_bpm: int = 60, max_bpm: int = 300, fps: int = 100
) -> Tuple[int, Generator[np.ndarray, None, None]]:
    """
    A generator that loads beats based on audio data itself, handling variations in tempo.
    This is a long, blocking, memory-intensive process! Setting ``online_mode`` to True may improve performance.

    :param fp: Path to or file-like object of the audio to load.
    :param min_bpm: Minimum permissible BPM.
    :param max_bpm: Maximum permissible BPM.
    :param fps: Resolution to process beats at.
    :return: A generator yielding each beat of the input song as a PyDub AudioSegment.
    """

    # Hefty imports! Let's wait until we use them.
    from madmom.features import DBNBeatTrackingProcessor, RNNBeatProcessor

    sig = Signal(fp)

    tracker = DBNBeatTrackingProcessor(min_bpm=min_bpm, max_bpm=max_bpm, fps=fps)
    processor = RNNBeatProcessor()
    times = tracker(processor(sig)) * sig.sample_rate

    def generator():
        last_x = 0
        for i, x in np.ndenumerate(times):
            x = int(x)
            yield sig[last_x:x, ...]
            last_x = x

    return sig.sample_rate, generator()


def load_beats_by_bpm(
    fp: Union[str, BinaryIO], bpm: int
) -> Tuple[int, Generator[np.ndarray, None, None]]:
    """
    A generator that loads beats strictly by a given BPM assuming no fluctuations in tempo. Significantly faster than
    `load_beats_by_signal` but far less accurate, especially in live performances.

    :param fp: Path to or file-like object of the audio to load.
    :param bpm: Song BPM. This can sometimes be found online.
    :return: A generator yielding each beat of the input song as a PyDub AudioSegment.
    """
    sig = Signal(fp)
    samples_per_beat = (60 * sig.sample_rate) // bpm

    def generator():
        for x in range(0, len(sig), samples_per_beat):
            yield sig[x + samples_per_beat, ...]

    return sig.sample_rate, generator()
