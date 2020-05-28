"""cogeo_mosaic_viewer.cli."""

import os

import click
from stac_viewer import app, stac


class MbxTokenType(click.ParamType):
    """Mapbox token type."""

    name = "token"

    def convert(self, value, param, ctx):
        """Validate token."""
        try:
            if not value:
                return ""

            assert value.startswith("pk")
            return value

        except (AttributeError, AssertionError):
            raise click.ClickException(
                "Mapbox access token must be public (pk). "
                "Please sign up at https://www.mapbox.com/signup/ to get a public token. "
                "If you already have an account, you can retreive your "
                "token at https://www.mapbox.com/account/."
            )


# add minzoom
# add maxzoom
@click.command()
@click.argument("stac_path", type=str)
@click.option(
    "--style",
    type=click.Choice(["satellite", "basic"]),
    default="basic",
    help="Mapbox basemap",
)
@click.option("--port", type=int, default=8080, help="Webserver port (default: 8080)")
@click.option(
    "--host",
    type=str,
    default="127.0.0.1",
    help="Webserver host url (default: 127.0.0.1)",
)
@click.option(
    "--mapbox-token",
    type=MbxTokenType(),
    metavar="TOKEN",
    default=lambda: os.environ.get("MAPBOX_ACCESS_TOKEN", ""),
    help="Mapbox token",
)
@click.option(
    "--exclude",
    type=str,
    default=["thumbnail"],
    multiple=True,
    help="Exclude assets (default: ['thumbnail'])",
)
@click.option(
    "--separate",
    is_flag=True,
    default=False,
    help="Consider each asset as separate band",
)
def viewer(stac_path, style, port, host, mapbox_token, exclude, separate):
    """
    Visualise STAC item in browser.

        Media-type of assets need to be one of:

            - image/tiff; application=geotiff

            - image/tiff; application=geotiff; profile=cloud-optimized

            - image/vnd.stac.geotiff; cloud-optimized=true

            - image/tiff

            - image/x.geotiff

            - image/jp2

            - application/x-hdf5

            - application/x-hdf

    """
    # Check if cog
    src_dst = stac.STACTiles(stac_path, exclude=exclude)
    application = app.vizStac(
        src_dst,
        token=mapbox_token,
        port=port,
        host=host,
        style=style,
        separate=separate,
    )

    url = application.get_template_url()
    click.echo(f"Viewer started at {url}", err=True)
    click.launch(url)
    application.start()
