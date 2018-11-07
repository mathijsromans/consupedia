from product.models import ProductScore, Brand, ScoreTheme, Certificate


class QuestionmarkMapper:

    @staticmethod
    def map_to_product(product, qm_entry):
        QuestionmarkMapper.map_brand(product, qm_entry)
        QuestionmarkMapper.extract_amount_from_name(product)
        QuestionmarkMapper.map_scores(product, qm_entry)
        QuestionmarkMapper.map_themes(product, qm_entry)
        product.thumb_url = qm_entry.thumb_url
        product.save()
        return product

    @staticmethod
    def map_brand(product, qm_entry):
        if qm_entry.brand:
            brand, created = Brand.objects.get_or_create(name=qm_entry.brand)
            product.brand = brand

    @staticmethod
    def extract_amount_from_name(product):
        amount = product.amount_from_name()
        if amount:
            product.set_amount(amount)

    @staticmethod
    def map_scores(product, qm_entry):
        scores, created = ProductScore.objects.get_or_create(product=product)
        scores.environment = qm_entry.score_environment
        scores.social = qm_entry.score_social
        scores.animals = qm_entry.score_animals
        scores.personal_health_score = qm_entry.score_personal_health
        scores.save()

    @staticmethod
    def map_themes(product, qm_entry):
        for qm_certificate in qm_entry.certificates.all():
            certificate, created = Certificate.objects.get_or_create(id=qm_certificate.id)
            certificate.name = qm_certificate.name
            certificate.image_url = qm_certificate.image_url
            for qm_theme in qm_certificate.themes.all():
                theme, created = ScoreTheme.objects.get_or_create(name=qm_theme.name)
                certificate.themes.add(theme)
            certificate.save()
            product.certificates.add(certificate)

