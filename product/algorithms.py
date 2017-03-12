from product.models import Product, UserPreferences, Category

class ProductScoring:
    def __init__(self, userweights, productScores):
        self.userweights = userweights
        self.productScores = productScores
        
    #returns the weighted sum over the user weights and the product scores    
    def calculateResult(self):
        result = 'DATA: '
        counter = 0
        sum = 0.0
        nrOfScores = 4
        sumOfUserWeights = 0.0
        while (counter < nrOfScores ):
            if(self.productScores[counter]):
                sum += self.productScores[counter] * self.userweights[counter]
                result += '(' + str(self.productScores[counter]) + ', '  + str(self.userweights[counter]) + ')'        
            else:
                sum += 4 * self.userweights[counter] #niet bekende score. Dan score 4, slechter dan gemiddelde.      
                result += '(n/a (4, '+ str(self.userweights[counter]) +')'                      
            sumOfUserWeights += self.userweights[counter]         
            counter += 1
            sumOfUserWeights = sumOfUserWeights or 1.0
        return sum / sumOfUserWeights, result #Som normaliseren door te delen door aantal scores.
            
class ProductChooseAlgorithm:
    @staticmethod
    def calculate_product_score(product, user_pref):
        if(product.scores):
            #price_weight niet in userweights.
            normalizedUserweights = user_pref.get_rel_weights()

            # todo: take price into account
            normalizedUserweights.pop(0)

            productScores = [product.scores.environment, product.scores.social, product.scores.animals, product.scores.personal_health]
            productScoring = ProductScoring(normalizedUserweights, productScores)
            return productScoring.calculateResult() 
        return 0, 'weetniet'
        
    @staticmethod
    def maximize_product_scores(user_pref, category):
        maxScore = -99999999999
        if Product.objects.all():
            productToReturn = Product.objects.all()[0]
            for product in Product.objects.all():
                if(product.category == category or not category):
                    result, test = ProductChooseAlgorithm.calculate_product_score(product, user_pref)
                    if result > maxScore:
                        maxScore = result
                        productToReturn = product
            return productToReturn
        return None

    @staticmethod
    def return_product(user_pref, category=None):
        return ProductChooseAlgorithm.maximize_product_scores(user_pref, category)

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

        