from product.models import Product


class ProductChooseAlgorithm:

    @staticmethod
    def return_product():
        return ProductChooseAlgorithm.cheapest_product()

    @staticmethod
    def cheapest_product():
        minPrice = 99999999999
        if Product.objects:
            productToReturn = Product.objects.all()[0]
            for product in Product.objects.all():
                price = product.price or 0
                if price < minPrice:
                    minPrice = price
                    productToReturn = product
            return productToReturn.name
        return None
