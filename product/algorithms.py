from product.models import Product, UserPreferences, Category

class ProductScoring:
    def __init__(self, userweights, productScores):
        self.userweights = userweights
        self.productScores = productScores        
        #normaliseren van de gebruikersgewichten.
        #voorbeeld : 6,2,4,1 => 1,0.3333,0.66666,0.
        maxval = max(self.userweights)
        normalizedUserweights = []
        for weight in self.userweights:         
            normalizedUserweights.append(float(weight / maxval))
        self.userweights = normalizedUserweights
        
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
        return sum / sumOfUserWeights, result #Som normaliseren door te delen door aantal scores.
            
class ProductChooseAlgorithm:    
    @staticmethod
    def calculate_product_score(product, user):   
        if(product.scores):
            #price_weight niet in userweights.
            userweights = [user.environment_weight, user.social_weight, user.animals_weight, user.personal_health_weight]
            productScores = [product.scores.environment, product.scores.social, product.scores.animals, product.scores.personal_health]
            productScoring = ProductScoring(userweights, productScores)
            return productScoring.calculateResult() 
        return 0, 'weetniet'
        
    @staticmethod
    def maximize_product_scores(user, category):
        maxScore = -99999999999
        if Product.objects.all():
            productToReturn = Product.objects.all()[0]
            for product in Product.objects.all():
                if(product.category == category or not category):
                    result, test = ProductChooseAlgorithm.calculate_product_score(product, user)
                    if result > maxScore:
                        maxScore = result
                        productToReturn = product
            return productToReturn.name + ', ' + str(maxScore)
        return None

    @staticmethod
    def return_product(user, category=None):
        return ProductChooseAlgorithm.maximize_product_scores(user, category)

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

        