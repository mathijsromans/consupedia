from collections import namedtuple
from .models import *
from product import settings


def get_user_scores(user):
    UserScore = namedtuple('UserScore', [
        'recipe_count',
        'sc_count',
        'recipe_count_score',
        'sc_count_score',
        'total_score'])
    recipe_count = Recipe.objects.filter(user=user).count()
    sc_count = ScoreCreator.objects.filter(user=user).count()
    recipe_count_score = recipe_count * settings.POINTS_PER_CREATED_RECIPE
    sc_count_score = sc_count * settings.POINTS_PER_CREATED_SCORE_CREATOR
    total_score = recipe_count_score + sc_count_score
    result = UserScore(
        recipe_count=recipe_count,
        sc_count=sc_count,
        recipe_count_score=recipe_count_score,
        sc_count_score=sc_count_score,
        total_score=total_score)
    return result
