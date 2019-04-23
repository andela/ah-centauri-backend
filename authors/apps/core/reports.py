from authors.apps.analytics.models import ReadsReport


def reporting(*args, **kwargs):
    """
    Handles reporting of visitors who clicked or read or clapped an article.
    :param request:
    :param kwargs:
    :return: [report]
    """
    try:
        report = ReadsReport.objects.get(user=kwargs.get('user'), article=kwargs.get('article'))
    except ReadsReport.DoesNotExist:
        report = ReadsReport.objects.create(user=kwargs.get('user'), article=kwargs.get('article'))

    return report
