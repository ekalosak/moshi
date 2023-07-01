from moshi import __version__

def render(template, request, **kwargs) -> 'html':
    """Add default routes to template from request.app.router; pass kwg to template.render()"""
    index_url = str(request.app.router['index'].url_for())
    news_url = str(request.app.router['news'].url_for())
    privacy_url = str(request.app.router['privacy'].url_for())
    html = template.render(
        version=f"alpha-{__version__}",
        index_url=index_url,
        news_url=news_url,
        privacy_url=privacy_url,
        **kwargs
    )
    return html
