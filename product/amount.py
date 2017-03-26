import re

class ProductAmount:
    NO_UNIT = '-'
    GRAM = 'g'
    ML = 'ml'
    EL = 'el'
    UNIT_CHOICES = (
        (NO_UNIT, 'st.'),
        (GRAM, 'g'),
        (ML, 'ml'),
        (EL, 'el')
    )

    def __init__(self, quantity, unit):
        self.quantity = quantity
        self.unit = unit

    @staticmethod
    def extract_size_substring(s):
        re_amount1 = re.compile('[0-9,]+ *(?:gram|liter)', re.IGNORECASE)
        re_amount2 = re.compile('[0-9,]+ *(?:g|ml|kg|l|cl)', re.IGNORECASE)
        sizes = re_amount1.findall(s) or re_amount2.findall(s)
        if sizes:
            return sizes[-1]
        return None

    @classmethod
    def from_str(cls, size):
        quantity = 0
        unit = ProductAmount.NO_UNIT

        size = size.replace(',', '.')
        numbers = re.findall(r'[-+]?\d*\.\d+|\d+', size)
        if numbers:
            nonnumbers = re.sub('[0-9\. ]', '', size)
            quantity, unit = ProductAmount.get_quantity_and_unit(float(numbers[0]), nonnumbers)
        return cls(quantity, unit)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return str(self.quantity) + ' ' + self.unit

    @staticmethod
    def get_quantity_and_unit(quantity, unit_text):
        if unit_text == '-' or unit_text == 'blaadjes' or unit_text == 'stuks':
            return quantity, ProductAmount.NO_UNIT
        if unit_text == 'g' or unit_text == 'gr' or unit_text == 'gram':
            return quantity, ProductAmount.GRAM
        if unit_text == 'kg':
            return 1000*quantity, ProductAmount.GRAM
        if unit_text == 'ml':
            return quantity, ProductAmount.ML
        if unit_text == 'cl':
            return 10*quantity, ProductAmount.ML
        if unit_text == 'l' or unit_text == 'L' or unit_text == 'liter':
            return 1000*quantity, ProductAmount.ML
        if unit_text == 'el':
            return quantity, ProductAmount.EL
        print('UNKNOWN UNIT : ' + unit_text)
        return int(quantity), ProductAmount.NO_UNIT
