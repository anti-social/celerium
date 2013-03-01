from flask import request, url_for


def current_url(**updates):
    kwargs = request.view_args.copy()
    kwargs.update(request.args)
    for k, v in updates.items():
        if v is None:
            kwargs.pop(k, None)
        else:
            kwargs[k] = v
    return url_for(request.endpoint, **kwargs)
