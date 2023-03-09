# Midjourney Downloader

Download your Midjourney gallery. Based on [midjourney-image-downloader](https://github.com/NickyReid/midjourney-image-downloader).

## Local Install

```bash
# Install
pip install -e .
# Run
mjdl --help
```

Output:

```bash
Usage: mjdl [OPTIONS]

Options:
  -u, --user_id TEXT              Your mj user id.  [required]
  -t, --token TEXT                Your mj session token (`__Secure-next-
                                  auth.session-token` cookie).  [required]
  -k, --kind [grids|upscales|all]
  -s, --sort-order [new|oldest|hot|rising|top-today|top-week|top-month|top-all|like_count]
  -o, --out PATH                  Base path where images are saved. [Default:
                                  pwd]
  --help                          Show this message and exit.

```

## Docker

### Build

```bash
docker build -t some-mjdl .
```

### Run

When you run in docker you likely want to use `--rm` to clean up the container. 

You probably also want to mount the volume so you can access the files on the host. The default output directory inside the container is `/jobs`.

```bash
$ docker run --rf \
    -v "$(pwd)/jobs:/jobs" \
    some-mjdl -u <some_user_id> -t <some_token>
```

## Automation

All command line arguments can also be specified via enviomnent variables by using the `MJDL_` prefix like so:

```bash
$ export MJDL_TOKEN="<some_token>"
$ export MJDL_USER_ID="<some_user_id>"

# Now run the command without passing those args...
$ mjdk --kind upscales

# Or with docker...
$ docker run --rm \
    -e MJDL_TOKEN='<some_token>' \
    -e MJDL_USER_ID='<some_user_id>' \
    some-mjdl --kind upscales
```