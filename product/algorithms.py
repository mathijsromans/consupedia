from product.models import Product


class ProductChooseAlgorithm:

	@staticmethod
	def return_product():
		return ProductChooseAlgorithm.cheapest_product()
	
	def 
		
	@staticmethod
	def cheapest_product():	
		minPrice = 99999999999
		if Product.objects:
			productToReturn = Product.objects.all()[0]
			for product in Product.objects.all():
				if product.price.cent < minPrice:
					minPrice = product.price.cent
					productToReturn = product
		
			return productToReturn.name
			
		return None
		
	#returns the weighted sum over the user weights and the product scores	
	@staticmethod
	def objective_function(product, userweights):
		counter = 0
		sum = 0
		while ( counter < len(product.Scores) ):
			sum += product.Scores[counter] * userweights[counter]
			counter++
		
		return sum
		
	@staticmethod
	def maximizeProductScores(userweights):
		maxScore = -99999999999
		if Product.objects:
			productToReturn = Product.objects.all()[0]
			for product in Product.objects.all():
				result = objective_function(product,userweights)
				if result > maxScore:
					maxScore = result
					productToReturn = product
		
			return productToReturn, result)
			
		return None
	
		
	
	
		
		
	

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
