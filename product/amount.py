import re
import logging


logger = logging.getLogger(__name__)


class ProductAmount:
    NO_UNIT = '-'
    GRAM = 'g'
    ML = 'ml'
    EL = 'el'
    TL = 'tl'
    UNIT_CHOICES = (
        (NO_UNIT, 'st.'),
        (GRAM, 'g'),
        (ML, 'ml'),
        (EL, 'el'),
        (TL, 'tl')
    )

    def __init__(self, quantity, unit):
        self.quantity = quantity
        self.unit = unit

    @staticmethod
    def extract_size_substring(s):
        re_amount1 = re.compile('[0-9,]+ *(?:gram|liter)', re.IGNORECASE)
        re_amount2 = re.compile('[0-9,]+ *(?:g|ml|kg|l|cl|stuk)', re.IGNORECASE)
        sizes = re_amount1.findall(s) or re_amount2.findall(s)
        if sizes:
            return sizes[-1]
        return None

    @classmethod
    def from_str(cls, size):
        quantity = 0
        unit = ProductAmount.NO_UNIT
        #logger.info('Amount from_str: {} ->'.format(size))
        
        ### remove the circa, ca.
        size = size.replace(',', '.')
        size = size.replace('ca', '')
        size = size.replace('ca.', '')
        size = size.replace('circa', '')
        size = size.replace('netje', '')

        # 'per stuk' -> '1 stuk'
        size = size.replace('per', '1')

        #logger.info('-> {}'.format(size))

        numbers = re.findall(r'[-+]?\d*\.\d+|\d+', size)
        if numbers:
            nonnumbers = re.sub('[0-9\. ]', '', size)
            quantity, unit = ProductAmount.get_quantity_and_unit(float(numbers[0]), nonnumbers)
        return cls(quantity, unit)

    @classmethod
    def normalise(cls, amount):
         quantity = amount.quantity
         unit = amount.unit
         if unit == ProductAmount.EL:
             unit = ProductAmount.ML
             quantity *= 15
         elif unit == ProductAmount.TL:
             unit = ProductAmount.ML
             quantity *= 5
         return cls(quantity, unit)


    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __truediv__(self, other):
        left = ProductAmount.normalise(self)
        right = ProductAmount.normalise(other)
        if left.unit != other.unit or right.quantity == 0:
            return 0
        return left.quantity / right.quantity

    def __str__(self):
        return str(self.quantity) + ' ' + self.unit


#### convert types of units to grams
    @staticmethod
    def get_quantity_and_unit(quantity, unit_text):
#### remove the first x from unitname
        unit_text = unit_text.lower()

        if unit_text[0:1] == 'x':
            unit_text = unit_text[1:]

        if unit_text == '-' or unit_text == 'blaadjes' or unit_text == 'stuks' or unit_text == 'krop' or unit_text == 'blaadje':
            return quantity, ProductAmount.NO_UNIT
        if unit_text == 'g' or unit_text == 'gr' or unit_text == 'gram':
            return quantity, ProductAmount.GRAM
        if unit_text == 'kg' or unit_text == 'kilo':
            return 1000*quantity, ProductAmount.GRAM
        if unit_text == 'ml':
            return quantity, ProductAmount.ML
        if unit_text == 'cl':
            return 10*quantity, ProductAmount.ML
        if unit_text == 'l' or unit_text == 'L' or unit_text == 'liter':
            return 1000*quantity, ProductAmount.ML
        if unit_text == 'el' or unit_text == 'eetlepels':
            return quantity, ProductAmount.EL
        if unit_text == 'tl' or unit_text == 'theelepels'or unit_text == 'theelepeltjes':
            return quantity, ProductAmount.TL
        if unit_text == 'pondje' or unit_text == 'pond':
            return 500*quantity, ProductAmount.GRAM
        if unit_text == 'ons' or unit_text == 'onsje':
            return 100*quantity, ProductAmount.GRAM
        if unit_text == 'snee' or unit_text == 'sneetje':
            return 80*quantity, ProductAmount.GRAM    
        if unit_text == 'blok' or unit_text == 'blokje':
            return 10*quantity, ProductAmount.GRAM    
    # this is a guess: a 'blik' is 400 gram and a 'blikje' is 100 gram
        if unit_text == 'blik':
            return 400*quantity, ProductAmount.GRAM    
        if unit_text == 'blikje':
            return 100*quantity, ProductAmount.GRAM    
        if unit_text == 'teen' or unit_text == 'teentje' or unit_text == 'tenen' or unit_text == 'teentjes':
            return 10*quantity, ProductAmount.GRAM
        if unit_text == '':
            return quantity,''
        print('QUANTITY: ' + str(quantity) + ', UNKNOWN UNIT: ' + unit_text)
        
        return int(quantity), ProductAmount.NO_UNIT


