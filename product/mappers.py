from product.models import Score, Brand

class QuestionmarkMapper:
    def map_to_product(self, product, product_dict):
        self.map_brand(product, product_dict)
        self.extract_amount_from_name(product)
        self.map_scores(product, product_dict)
        self.map_urls(product, product_dict)

        product.save()
        return product

    @staticmethod
    def map_brand(product, product_dict):
        if product_dict['brand'] and product_dict['brand']['name']:
            brand, created = Brand.objects.get_or_create(name=product_dict['brand']['name'])
            product.brand = brand

    @staticmethod
    def extract_amount_from_name(product):
        amount = product.amount_from_name()
        if amount:
            product.set_amount(amount)

    @staticmethod
    def map_urls(product, product_dict):
        if 'image_urls' in product_dict:
            urls = product_dict['image_urls']
            for url in urls:
                if 'thumb' in url:
                    product.thumb_url = url['thumb']

    @staticmethod
    def map_scores(product, product_dict):
        theme_scores = product_dict["theme_scores"]
        personal_health_score = product_dict["personal_health_score"]

        if theme_scores or personal_health_score:
            product.scores = Score.objects.create()

        if theme_scores:
            for score in theme_scores:
                if score["theme_key"] == "environment":
                    product.scores.environment = score["score"]
                elif score["theme_key"] == "social":
                    product.scores.social = score["score"]
                elif score["theme_key"] == "animals":
                    product.scores.animals = score["score"]
        if personal_health_score:
            product.scores.personal_health_score = personal_health_score

        if product.scores:
            product.scores.save()