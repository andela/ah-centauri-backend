from authors.apps.analytics.models import ReadsReport


def reporting(*args, **kwargs):
    """
    Handles reporting of visitors who clicked or read or clapped an article.
    :param request:
    :param kwargs:
    :return: [report]
    """
    report = ReadsReport.objects.create(**kwargs)
    return report
