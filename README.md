# Midjourney Downloader

Download your Midjourney gallery. Based on [midjourney-image-downloader](https://github.com/NickyReid/midjourney-image-downloader).

## Local Install
 ```bash
 $ pip install -e .
 ```

Then run  it

```bash
$ mjdl --help
```

## Docker

### Build

```bash
$ docker build -t some-mjdl .
```

### Run

```bash
$ docker run --rf some-mjdl
```