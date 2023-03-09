#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import click
import sys
from pathlib import Path
from src import Downloader, DownloadKind

@click.command(context_settings={"auto_envvar_prefix": "MJDL"})
@click.option('--user_id', '-u', type=str, required=True, help='Your mj user id.')
@click.option('--token', '-t', required=True, type=str, help='Your mj session token (`__Secure-next-auth.session-token` cookie).')
@click.option('--kind', '-k', type=click.Choice(['grids', 'upscales', 'all'], case_sensitive=False))
@click.option('--sort-order', '-s', 'sort_oder',type=click.Choice(["new", "oldest", "hot", "rising", "top-today", "top-week", "top-month", "top-all", "like_count"], case_sensitive=False), default="new")
@click.option('--out', '-o', 'out_path', type=click.Path(path_type=Path), required=False, default=(Path().absolute() / 'jobs'), help='Base path where images are saved. [Default: pwd]')
def cli(user_id: str, kind: str, token: str, sort_oder: str, out_path: Path):
	downloader = Downloader(user_id, token)
	download_kind = DownloadKind[kind]
	click.echo("Starting download...")
	downloader.download(download_kind, sort_oder, out_path, True, True, False)


if __name__ == "__main__":
	sys.exit(cli())