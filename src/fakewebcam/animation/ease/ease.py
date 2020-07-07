#!/usr/bin/env python

import rx
from rx import operators as op
from ...common.size import Size

def ease(factory, start, end, frame_rate, duration):
        ease = factory(start=start, end=end, duration=frame_rate * duration)
        return rx.from_iterable(range(0, int(frame_rate * duration))).pipe(op.map(ease.ease))

def ease_size(factory, start_size, end_size, frame_rate, duration):
    heights = ease(factory, start=start_size.height, end=end_size.height, frame_rate=frame_rate, duration=duration)
    widths = ease(factory, start=start_size.width, end=end_size.width, frame_rate=frame_rate, duration=duration)

    return widths.pipe(op.zip(heights), op.map(lambda t: Size(int(t[0]), int(t[1]))))