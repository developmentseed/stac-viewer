"""rio_viz.raster: raster tiles object."""

from concurrent import futures
from typing import Any, Dict, Sequence, Tuple

import numpy
import requests
from rio_tiler.io import stac as STACTiler
from rio_tiler.io.cogeo import info as cogInfo

valid_type = [
    "image/tiff; application=geotiff",
    "image/tiff; application=geotiff; profile=cloud-optimized",
    "image/vnd.stac.geotiff; cloud-optimized=true",
    "image/tiff",
    "image/x.geotiff",
    "image/jp2",
    "application/x-hdf5",
    "application/x-hdf",
]


class STACTiles(object):
    """STAC tiles object."""

    def __init__(
        self, src_path: str, include: Sequence[str] = [], exclude: Sequence[str] = []
    ):
        """Initialize STACTiles object."""
        self.path = src_path

        # TODO HANDLE LOCAL / S3 files
        self.item: Dict[str, Any] = requests.get(src_path).json()

        self.asset_names: Sequence[str] = [
            asset
            for asset, info in self.item["assets"].items()
            if asset not in exclude and info["type"] in valid_type
        ]

        self.bounds = self.item["bbox"]

    def read_tile(
        self,
        z: int,
        x: int,
        y: int,
        assets: Sequence[str],
        tilesize: int = 256,
        resampling_method: str = "bilinear",
        **kwargs: Any,
    ) -> Tuple[numpy.ndarray, numpy.ndarray]:
        """Read raster tile data and mask."""
        return STACTiler.tile(
            self.item,
            assets,
            x,
            y,
            z,
            tilesize=tilesize,
            resampling_method=resampling_method,
            **kwargs,
        )

    def info(self) -> Dict:
        """Return general info about the images."""
        assets_url = STACTiler._get_href(self.item, self.asset_names)

        with futures.ThreadPoolExecutor() as executor:
            res = list(executor.map(cogInfo, assets_url))

        return {
            "bounds": self.bounds,
            "assets": {asset: res[ix] for ix, asset in enumerate(self.asset_names)},
        }
