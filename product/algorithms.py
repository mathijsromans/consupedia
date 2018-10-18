def generate_sorted_list(product_list, user_preferences):
    products_and_scores = [(product,  product.score(user_preferences)) for product in product_list]
    products_and_scores.sort(key=lambda x: x[1].total())
    return products_and_scores


class ProductChooseAlgorithm:
    @staticmethod
    def calculate_product_score(product, user_pref):
        result = None
        if product.price:
            price = product.price.price
            if product.quantity:
                price /= product.quantity
            product_scores_dict = {}
            if product.scores:
                product_scores_dict.update(product.scores.get_dict())
            product_scores_dict['price'] = price
            result = Score(user_pref)
            result.scores = product_scores_dict
        return result
        
    @staticmethod
    def maximize_product_scores(user_pref, food=None):
        maxScore = -99999999999
        if Product.objects.all():
            productToReturn = Product.objects.all()[0]
            for product in Product.objects.all():
                if product.food == food or not food:
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

from .models import Score, Product