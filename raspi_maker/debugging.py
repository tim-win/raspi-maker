import pdb
import traceback


class PromptOnError(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        try:
            return self.func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()

            print 'Falling back to prompt to try live fix.'
            print 'c to continue when things look ok again.'
            print 'exit() to gtfo and cancel.'

            pdb.set_trace()
