from product.models import Product, UserPreferences

class ProductChooseAlgorithm:    
    #returns the weighted sum over the user weights and the product scores    
    @staticmethod
    def objective_function(productScores, userweights):
        counter = 0
        sum = 0
        nrOfScores = 4
        while ( counter < nrOfScores ):
            if(productScores[counter]):
                sum += productScores[counter] * userweights[counter]
            else:
                sum += 4 #niet bekende score. Dan score 4, slechter dan gemiddelde.             
            counter+=1        
        return sum / nrOfScores #Som normaliseren door te delen door aantal scores.
        
    @staticmethod
    def maximize_product_scores(user):
        maxScore = -99999999999
        if Product.objects.all():
            productToReturn = Product.objects.all()[0]
            for product in Product.objects.all():
                if(product.scores):
                    #price_weight niet in userweights.
                    userweights = [user.environment_weight, user.social_weight, user.animals_weight, user.personal_health_weight]
                    productScores = [product.scores.environment, product.scores.social, product.scores.animals, product.scores.personal_health]
                    result = ProductChooseAlgorithm.objective_function(productScores, userweights)
                    if result > maxScore:
                        maxScore = result
                        productToReturn = product
                    return productToReturn.name + ', ' + str(result)
        return None

    @staticmethod
    def return_product(user):
        return ProductChooseAlgorithm.maximize_product_scores(user)

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

        