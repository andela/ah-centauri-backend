import json

from rest_framework.renderers import JSONRenderer


class CommentJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        # If the view throws an error (such as the user can't be authenticated
        # or something similar), `data` will contain an `errors` key. We want
        # the default JSONRenderer to handle rendering errors, so we need to
        # check for this case.
        if isinstance(data, dict):
            errors = data.get('errors', None)

            if errors is not None:
                # As mentioned about, we will let the default JSONRenderer handle
                # rendering errors.
                return json.dumps(data)

        if isinstance(data, list):
            return json.dumps({
                "comments": data,
                'commentsCount': len(data),
            })
        return json.dumps({
            "comment": data,
        })
