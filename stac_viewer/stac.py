"""stac_viewer.stac: handler for STAC."""

from typing import Any, Dict, Sequence, Tuple

import numpy

from stac_tiler import STACReader


class STACTiles(object):
    """STAC tiles object."""

    def __init__(self, src_path: str, **kwargs):
        """Initialize STACTiles object."""
        self.path = src_path
        with STACReader(self.path, **kwargs) as stac:
            self.assets = stac.assets
            self.stac = stac

    @property
    def bounds(self):
        """bounds."""
        return self.stac.bounds

    def read_tile(
        self, z: int, x: int, y: int, assets: Sequence[str], **kwargs: Any,
    ) -> Tuple[numpy.ndarray, numpy.ndarray]:
        """Read raster tile data and mask."""
        return self.stac.tile(x, y, z, assets=assets, **kwargs)

    def info(self) -> Dict:
        """Return general info about the images."""
        info = self.stac.info(self.assets)
        return {"bounds": self.stac.bounds, "assets": info}
