from .models import Product, Score, Category

class QuestionmarkMapper:
    def map_to_product(self, product, product_dict):
        self.map_scores(product, product_dict)
        self.map_usages(product, product_dict)

        product.save()
        return product

    def map_usages(self, product, product_dict):
        usages = product_dict["usages"]

        if usages:
            newCategory = usages[-1]
            category, created = Category.objects.get_or_create(name=newCategory['name'])
            product.category = category


    def map_scores(self, product, product_dict):
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

