"""rio-viz: Template Factory."""

import os
from typing import Callable

from starlette.requests import Request
from starlette.templating import Jinja2Templates, _TemplateResponse

html_templates = Jinja2Templates(directory=os.path.dirname(__file__))


def create_index_template_factory(
    tilejson: str = "stac_tilejson", info: str = "stac_info"
) -> Callable[[Request], _TemplateResponse]:
    """
    Create a dependency which may be injected into a FastAPI app.  The input parameters are used to look up the specific
    URLs for each route.
    """

    def _template(request: Request) -> _TemplateResponse:
        """Create a template of ``templates/index.html`` from a request"""
        return html_templates.TemplateResponse(
            name="index.html",
            context={
                "request": request,
                # https://github.com/encode/starlette/blob/master/docs/routing.md#reverse-url-lookups
                # `request.url_for` will reconstruct the full URL path based on
                # the `name` of the route which here is the function name.
                "tilejson_endpoint": request.url_for(tilejson),
                "info_endpoint": request.url_for(info),
                # Mapbox parameters default to those defined in the CLI
                # These are overridden in the app itself
                "mapbox_token": "",
                "mapbox_style": "basic",
            },
            media_type="text/html",
        )

    return _template


index_template_factory = create_index_template_factory()
