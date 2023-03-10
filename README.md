# Midjourney Downloader

The Midjourney Downloader is a Python package that enables you to download all of your Midjourney gallery. This package is based on [midjourney-image-downloader](https://github.com/NickyReid/midjourney-image-downloader).

## Local Installation

You can install the Midjourney Downloader package locally by running the following command:

```bash
pip install -e .
```

To run the package, use the following command:

```bash
mjdl --help
```

This command will output the usage options for the package:

```bash
Usage: mjdl [OPTIONS]

Options:
  -u, --user_id TEXT              Your mj user id.  [required]
  -t, --token TEXT                Your mj session token (`__Secure-next-
                                  auth.session-token` cookie).  [required]
  -k, --kind [grids|upscales|all]
  -s, --sort-order [new|oldest|hot|rising|top-today|top-week|top-month|top-all|like_count]
                                  Sort order by which to download images.
                                  [default: new]
  -a, --aggregate-by [prompt|month|day]
                                  The folder aggregation strategy.  [default:
                                  day]
  -m, --save-models               Save the JSON model along with the image.
  -p, --save-prompt               Save the prompt as `prompt.txt`
  -c, --save-command              Save the full command as `command.txt`
  -r, --skip-low-rated            Skip downloading low-rated images.
  -o, --out PATH                  Base path where images are saved.  [default:
                                  `pwd`]
  --help                          Show this message and exit.
```

## Folder Aggregation

There are three options for how to aggregate data into folders locally:

- `day`: Saves data under `<base_path>/<year>/<month>/<day>/<prompt>.png`
- `month`: Saves data under `<base_path>/<year>/<month>/<prompt>.png`
- `prompt`: Saves data under `<base_path>/<prompt>/<image_id>.png`

## Docker

### Build

You can build a Docker image for the Midjourney Downloader by running the following command:

```bash
docker build -t some-mjdl .
```

### Run

If you want to run the Midjourney Downloader inside a Docker container, you can use the following command:

```bash
$ docker run --rf \
    -v "$(pwd)/jobs:/jobs" \
    some-mjdl -u <some_user_id> -t <some_token>
```

When running in Docker, you should use the `--rm` flag to clean up the container after use. Additionally, you should mount a volume so that you can access the downloaded files on the host. By default, the downloaded images will be saved in the `/jobs` directory inside the container.

## Automation

All command line arguments can be specified as environment variables by using the `MJDL_` prefix. For example:

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

## License

MIT