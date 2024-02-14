class AppError(Exception):
    """
    Base class for application logic errors.
    """
    msg_template: str = None

    def __init__(self, **kwargs):
        self.context = kwargs.pop('context', {})

        if 'message' in kwargs:
            self.message = kwargs['message']
        elif self.msg_template:
            self.message = self.msg_template.format(**kwargs)
        else:
            self.message = None

    def __str__(self):
        return self.message
