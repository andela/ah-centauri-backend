from .models import Highlights


def remove_highlights_for_article(article):
    """
    Remove all highlights for a specific article
    :param article:
        An instance of the Articles model
    :return:
        Returns True if the highlights were deleted
        Returns None if there were no highlights to delete
    """
    article_highlights = Highlights.objects.filter(
        article=article
    )
    if len(article_highlights) < 1:
        return None
    for highlight in article_highlights:
        highlight.delete()
    return True
