"""stac viewer app."""

from typing import Any, Optional

import os
import re
import urllib.parse
from starlette.requests import Request
from starlette.responses import Response, HTMLResponse
from starlette.templating import Jinja2Templates

from rio_viz.app import viz as BaseVizClass

from rio_viz.raster import postprocess_tile
from rio_tiler.utils import render
from rio_viz.models.mapbox import TileJSON
from rio_tiler.colormap import get_colormap
from rio_tiler.profiles import img_profiles

from rio_viz.ressources.enums import ImageType
from rio_viz.ressources.common import drivers, mimetype
from rio_viz.ressources.responses import TileResponse

from fastapi import Depends, Query
from functools import partial

from starlette.concurrency import run_in_threadpool
from starlette.templating import _TemplateResponse

from stac_viewer.templates.template import index_template_factory


dir = os.path.dirname(__file__)
templates = Jinja2Templates(directory=f"{dir}/templates")

_postprocess_tile = partial(run_in_threadpool, postprocess_tile)
_render = partial(run_in_threadpool, render)


class vizStac(BaseVizClass):
    """Creates a very minimal slippy map tile server using fastAPI + Uvicorn."""

    separate: bool

    def __init__(self, *args, separate: bool = False, **kwargs):
        """Overwrite base class."""
        super(vizStac, self).__init__(*args, **kwargs)

        self.separate = separate

        @self.app.get(
            "/stac/index.html",
            responses={200: {"description": "Simple COG viewer."}},
            response_class=HTMLResponse,
        )
        def stac_viewer(template: _TemplateResponse = Depends(index_template_factory)):
            """Handle /index.html."""
            template.context.update(
                {"mapbox_access_token": self.token, "mapbox_style": self.style}
            )
            return template

        @self.app.get(
            r"/stac/tiles/{z}/{x}/{y}",
            responses={
                200: {
                    "content": {"image/png": {}, "image/jpg": {}, "image/webp": {}},
                    "description": "Return an image.",
                }
            },
            response_class=TileResponse,
            description="Read COG and return a tile",
        )
        @self.app.get(
            r"/stac/tiles/{z}/{x}/{y}\.{ext}",
            responses={
                200: {
                    "content": {"image/png": {}, "image/jpg": {}, "image/webp": {}},
                    "description": "Return an image.",
                }
            },
            response_class=TileResponse,
            description="Read COG and return a tile",
        )
        async def stac_tile(
            z: int,
            x: int,
            y: int,
            scale: int = Query(2, gt=0, lt=4),
            ext: ImageType = None,
            assets: Any = Query(None, description="Coma (',') delimited band indexes"),
            indexes: Any = Query(None, description="Coma (',') delimited band indexes"),
            rescale: Any = Query(
                None, description="Coma (',') delimited Min,Max bounds"
            ),
            color_formula: str = Query(None, description="rio-color formula"),
            color_map: str = Query(None, description="rio-tiler color map names"),
            resampling_method: str = Query(
                "bilinear", description="rasterio resampling"
            ),
        ):
            """Handle /tiles requests."""
            if isinstance(assets, str):
                assets = assets.split(",")

            if isinstance(indexes, str):
                indexes = tuple(int(s) for s in re.findall(r"\d+", indexes))

            tilesize = scale * 256
            tile, mask = self.raster.read_tile(
                z,
                x,
                y,
                assets,
                tilesize=tilesize,
                indexes=indexes,
                resampling_method=resampling_method,
            )

            tile = await _postprocess_tile(
                tile, mask, rescale=rescale, color_formula=color_formula
            )

            if color_map:
                color_map = get_colormap(color_map)

            if not ext:
                ext = ImageType.jpg if mask.all() else ImageType.png

            driver = drivers[ext]
            options = img_profiles.get(driver.lower(), {})
            content = await _render(
                tile, mask, colormap=color_map, img_format=driver, **options
            )
            return TileResponse(content, media_type=mimetype[ext.value])

        @self.app.get(
            "/stac/tilejson.json",
            response_model=TileJSON,
            responses={200: {"description": "Return a tilejson"}},
            response_model_include={
                "tilejson",
                "scheme",
                "version",
                "minzoom",
                "maxzoom",
                "bounds",
                "center",
                "tiles",
            },  # https://github.com/tiangolo/fastapi/issues/528#issuecomment-589659378
        )
        def stac_tilejson(
            request: Request,
            response: Response,
            tile_format: Optional[ImageType] = None,
            minzoom: Optional[int] = 0,
            maxzoom: Optional[int] = 22,
        ):
            """Handle /tilejson.json requests."""
            scheme = request.url.scheme
            host = request.headers["host"]

            kwargs = dict(request.query_params)
            kwargs.pop("tile_format", None)
            kwargs.pop("minzoom", None)
            kwargs.pop("maxzoom", None)

            tile_url = f"{scheme}://{host}/stac/tiles/{{z}}/{{x}}/{{y}}"
            if tile_format:
                tile_url += f".{tile_format}"

            qs = urllib.parse.urlencode(list(kwargs.items()))
            if qs:
                tile_url += f"?{qs}"

            center = [
                (self.raster.bounds[0] + self.raster.bounds[2]) / 2,
                (self.raster.bounds[1] + self.raster.bounds[3]) / 2,
                minzoom,
            ]

            return dict(
                bounds=self.raster.bounds,
                center=center,
                minzoom=minzoom,
                maxzoom=maxzoom,
                name="rio-viz",
                tilejson="2.1.0",
                tiles=[tile_url],
            )

        @self.app.get("/stac/info")
        def stac_info():
            """Handle /info requests."""
            return {**dict(separate=self.separate, **self.raster.info())}

    def get_template_url(self) -> str:
        """Get simple app template url."""
        return f"http://{self.host}:{self.port}/stac/index.html"
