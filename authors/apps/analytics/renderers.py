import json

from rest_framework.renderers import JSONRenderer


class AnalyticsJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        # If the view throws an error (such as the user can't be authenticated
        # or something similar), `data` will contain an `errors` key. We want
        # the default JSONRenderer to handle rendering errors, so we need to
        # check for this case.

        if isinstance(data, list):
            return json.dumps({
                "views": data,
                'viewsCount': len(data),
            })
        return json.dumps(data)
