from django.db.models import Func


class Round(Func):
    function = 'ROUND'
    arity = 2
    template = '%(function)s(%(expressions)s)'
