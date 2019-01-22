import copy
import collections
from enum import Enum
import logging

logger = logging.getLogger(__name__)


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
    def __init__(self, value, food_property_type=None):
        2+value  # check that value is a number
        self.value = value
        self.food_property_type = food_property_type

    def is_scaling(self):
        return self.food_property_type.is_scaling()

    def scale(self, scalar):
        if self.is_scaling():
            self.value *= scalar

    def add(self, v):
        print('adding {}+{}={}'.format(self.value, v, self.value+v))
        self.value += v

    def __str__(self):
        return '{} -> {}'.format(self.food_property_type, self.value)


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

    def add(self, other, quantity):
        for key, svalue in other.get_dict().items():
            self.add_food_property_type_and_value(svalue.food_property_type, svalue.value, quantity)

    def add_food_property(self, food_property, quantity):
        self.add_food_property_type_and_value(food_property.type, food_property.value_bool, quantity)

    def add_food_property_type_and_value(self, food_property_type, food_property_value, quantity):
        # logger.info('add_food_property_type_and_value {}: {} ({})'.format(food_property_type, food_property_value, quantity))
        key = food_property_type.name
        try:
            old_value = self._scores[key]
            new_value = food_property_type.combine(old_value.value, food_property_value, quantity)
        except KeyError:
            new_value = food_property_value
        self._scores[key] = ScoreValue(new_value, food_property_type)

    def override(self, food_property):
        self.set(food_property.type, food_property.value)

    def set(self, food_property_type, food_property_value):
        key = food_property_type.name
        self._scores[key] = ScoreValue(food_property_value, food_property_type)

    @property
    def price(self):
        return Price(self.get_or_0('prijs'))

    @property
    def land_use_m2(self):
        return self.get_or_0('landgebruik')

    @property
    def animal_harm(self):
        return self.get_or_0('dierenleed')

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
