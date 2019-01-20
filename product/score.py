import copy
import collections
from enum import Enum


class ReadonlyDictWrapper(collections.Mapping):

    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)


class Price:
    def __init__(self, cents):
        self.cents = cents

    def __mul__(self, other):
        return Price(self.cents * other)

    def __str__(self):
        if self.cents:
            return '€ {:03.2f}'.format(self.cents/100.0)
        return '€ ?'


class ScoreValue:
    class ScalingProperty(Enum):
        NormalScale = 1
        NoScale = 2

    def __init__(self, value, scale_property):
        2+value  # check that value is a number
        self.value = value
        self.scale_property = scale_property

    def scale(self, scalar):
        if self.scale_property == ScoreValue.ScalingProperty.NormalScale:
            self.value *= scalar

    def add(self, v):
        print('adding {}+{}={}'.format(self.value, v, self.value+v))
        self.value += v


class Score:
    def __init__(self, user_pref):
        self.user_pref = user_pref
        self._scores = {}

    def __lt__(self, other):
        return self.total < other.total

    def scale(self, scalar):
        for value in self._scores.values():
            value.scale(scalar)

    def scaled(self, scalar):
        result = copy.deepcopy(self)
        result.scale(scalar)
        return result

    def add(self, other):
        for key, svalue in other.get_dict().items():
            self.add_score(key, svalue.value, svalue.scale_property)

    def add_score(self, key, value, scale_property=ScoreValue.ScalingProperty.NormalScale):
        if not key or value is None:
            return
        if key in self._scores:
            self._scores[key].add(value)
        else:
            self._scores[key] = ScoreValue(value, scale_property)
        assert(key != 'prep_time' or scale_property==ScoreValue.ScalingProperty.NoScale)

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
        return self._scores[key].value

    def get_or_0(self, key):
        try:
            return self.get(key)
        except KeyError:
            return 0

    def get_dict(self):
        return ReadonlyDictWrapper(self._scores)

    @property
    def total(self):
        result = 0
        user_pref_dict = self.user_pref.get_dict()
        for key, svalue in self._scores.items():
            user_pref_value = user_pref_dict.get(key, 0.0)
            result += svalue.value * user_pref_value
        return result

    def __str__(self):
        result = ''
        user_pref_dict = self.user_pref.get_dict()
        for key, svalue in self._scores.items():
            user_pref_value = user_pref_dict.get(key, 0.0)
            partial = svalue.value * user_pref_value
            result += '[{}: {:.2f} -> {:.2f}] '.format(key, svalue.value, partial)
        result += '-> {:.2f}'.format(self.total)
        return result
