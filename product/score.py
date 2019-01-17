

class Price:
    def __init__(self, cents):
        self.cents = cents

    def __mul__(self, other):
        return Price(self.cents * other)

    def __str__(self):
        if self.cents:
            return '€ {:03.2f}'.format(self.cents/100.0)
        return '€ ?'


class Score:
    def __init__(self, user_pref):
        self.user_pref = user_pref
        self._scores = {}

    def __lt__(self, other):
        return self.total < other.total

    def scale(self, scalar):
        for key, value in self._scores.items():
            self._scores[key] = scalar * value

    def scaled(self, scalar):
        result = copy.deepcopy(self)
        result.scale(scalar)
        return result

    def add(self, other):
        for key, value in other._scores.items():
            self.add_score(key, value)

    def add_score(self, key, value):
        if not key or value is None:
            return
        if key in self._scores:
            self._scores[key] += value
        else:
            self._scores[key] = value

    @property
    def price(self):
        return Price(self.get_or_0('price'))

    @property
    def land_use_m2(self):
        return self.get_or_0('land_use_m2')

    @property
    def animal_harm(self):
        return self.get_or_0('animal_harm')

    def get(self, key):
        return self.get(key)

    def get_or_0(self, key):
        value = self._scores.get(key)
        return value if value is not None else 0

    @property
    def total(self):
        result = 0
        user_pref_dict = self.user_pref.get_dict()
        for key, value in self._scores.items():
            user_pref_value = user_pref_dict.get(key, 1.0)
            if user_pref_dict and value is not None:
                result += value * user_pref_value
        return result

    def __str__(self):
        result = ''
        user_pref_dict = self.user_pref.get_dict()
        for key, value in self._scores.items():
            user_pref_value = user_pref_dict.get(key, 1.0)
            if user_pref_dict and value is not None:
                partial = value * user_pref_value
                result += '[{}: {:.2f} -> {:.2f}] '.format(key, value, partial)
        result += '-> {:.2f}'.format(self.total)
        return result