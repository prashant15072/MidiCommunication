# -*- coding: utf-8 -*-

__all__ = ('yieldsleep', )

from functools import wraps
from kivy.clock import Clock

schedule_once = Clock.schedule_once


def yieldsleep(create_gen):
    @wraps(create_gen)
    def func(*args, **kwargs):
        gen = create_gen(*args, **kwargs)

        def sleep(seconds):
            schedule_once(resume_gen, seconds)

        def resume_gen(dt):
            try:
                sleep(gen.send(dt))
            except StopIteration:
                pass

        try:
            sleep(next(gen))
        except StopIteration:
            pass
        return gen
    return func


def _test():
    from kivy.app import runTouchApp
    from kivy.factory import Factory

    root = Factory.Label(
        text='Hello', font_size='100sp', markup=True,
        outline_color=(1, 1, 1, 1, ), outline_width=2,
    )

    @yieldsleep
    def animate_label(label, times):
        yield 0
        for __ in range(times):
            label.text = 'Do'
            label.color = (0, 0, 0, 1, )
            dt = yield .5
            print('{:.2f}s passed'.format(dt))
            label.text = 'You'
            dt = yield .5
            print('{:.2f}s passed'.format(dt))
            label.text = 'Like'
            dt = yield .5
            print('{:.2f}s passed'.format(dt))
            label.text = 'Kivy?'
            dt = yield 2
            print('{:.2f}s passed'.format(dt))
            label.text = 'Answer me!'
            label.color = (1, 0, 0, 1, )
            dt = yield 3
            print('{:.2f}s passed'.format(dt))

    gen = animate_label(root, times=5)

    def on_touch_down(label, touch):
        gen.close()
        label.text = 'The animation\nwas cancelled.'
        label.color = (.5, 0, .5, 1, )
    root.bind(on_touch_down=on_touch_down)
    runTouchApp(root)


if __name__ == "__main__":
    _test()