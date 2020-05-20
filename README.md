# stac-viewer

!! WORK IN PROGRESS !! 

Visualize [STAC](https://stacspec.org) items in browser.

### Install

```bash
$ pip install git+https://github.com/developmentseed/stac-viewer.git
```

#### CLI
```bash 
$ stac-viewer --help
Usage: stac-viewer [OPTIONS] STAC_PATH

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

Options:
  --style [satellite|basic]  Mapbox basemap
  --port INTEGER             Webserver port (default: 8080)
  --host TEXT                Webserver host url (default: 127.0.0.1)
  --mapbox-token TOKEN       Mapbox token
  --exclude TEXT             Exclude assets (default: ['thumbnail'])
  --separate                 Consider each asset as separate band
  --help                     Show this message and exit.
```

#### Examples
```bash
$ stac-viewer https://storage.googleapis.com/pdd-stac/disasters-0.9.0/hurricane-harvey/0831/20170831_162740_ssc1d1.json

$ AWS_REQUEST_PAYER="requester" stac-viewer https://raw.githubusercontent.com/radiantearth/stac-spec/master/item-spec/examples/CBERS_4_MUX_20181029_177_106_L4.json --separate
```