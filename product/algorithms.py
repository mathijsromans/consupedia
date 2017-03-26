from product.models import Product


class ScoreResult:

    def __init__(self):
        self.score = []

    def add_score(self, score, descr):
        self.score.append((score, descr))

    def total(self):
        result = 0
        for s in self.score:
            result += s[0]
        return result

    def __str__(self):
        result = ''
        for s in self.score:
            result += ' ' + s[1]
        return result

def set_score(product, user_preferences):
    score = ProductChooseAlgorithm.calculate_product_score(product, user_preferences)
    if score:
        product.product_score = score.total()
        product.product_score_details = str(score)

def generate_sorted_list(product_list, user_preferences):
    for product in product_list:
        set_score(product, user_preferences)
    product_list = list(product_list)
    product_list = [p for p in product_list if p.product_score]
    product_list.sort(key= lambda x: x.product_score if x.product_score else -99999999, reverse=True)
    return product_list


def score_product(userweights, product_scores):
    result = ScoreResult()
    counter = 0
    while counter < len(product_scores):
        if product_scores[counter]:
            score = product_scores[counter] * userweights[counter]
            descr = '({:.2f}, {:.2f}->{:.2f})'.format(product_scores[counter], userweights[counter], score)
            result.add_score(score, descr)
        else:
            score = 4 * userweights[counter]  # niet bekende score. Dan score 4, slechter dan gemiddelde.
            descr = '(n/a, {:.2f}->{:.2f})'.format(userweights[counter], score)
            result.add_score(score, descr)
        counter += 1
    return result


class ProductChooseAlgorithm:
    @staticmethod
    def calculate_product_score(product, user_pref):
        result = None
        if product.price:
            product_scores = [0, 0, 0, 0]
            if product.scores:
                product_scores = [product.scores.environment, product.scores.social, product.scores.animals, product.scores.personal_health]
            normalizedUserweights = user_pref.get_rel_weights()
            price_weight = normalizedUserweights.pop(0)
            result = score_product(normalizedUserweights, product_scores)
            score = -product.price.price * price_weight
            descr = '(' +str(product.price) + ', {:.2f}->{:.2f})'.format(price_weight, score)
            result.add_score(score, descr)
        return result
        
    @staticmethod
    def maximize_product_scores(user_pref, category=None):
        maxScore = -99999999999
        if Product.objects.all():
            productToReturn = Product.objects.all()[0]
            for product in Product.objects.all():
                if product.category == category or not category:
                    result = ProductChooseAlgorithm.calculate_product_score(product, user_pref)
                    if result and result.total() > maxScore:
                        maxScore = result.total()
                        productToReturn = product
            return productToReturn
        return None

    @staticmethod
    def cheapest_product():
        minPrice = 99999999999
        if Product.objects.all():
            productToReturn = Product.objects.all()[0]
            for product in Product.objects.all():
                price = product.price or 999999999999
                if price < minPrice:
                    minPrice = price
                    productToReturn = product
            return productToReturn.name
        return None

