from moshi import __version__

def render(template, request) -> 'html':
    privacy_url = str(request.app.router['privacy'].url_for())
    news_url = str(request.app.router['news'].url_for())
    html = template.render(
        version=f"alpha-{__version__}",
        privacy_url=privacy_url,
        news_url=news_url,
    )
    return html
