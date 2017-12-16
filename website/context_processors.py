from website import __version__


def info(request):
    return {
        'is_anonymous_user': request.user.groups.filter(name='anonymous').exists(),
        'project_version': __version__
    }

