from product.models import Price, Product

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
				if product.price.cent < minPrice:
					minPrice = product.price.cent
					productToReturn = product
		
			return productToReturn.name
			
		return None
			
		

	