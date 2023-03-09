#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import click
import sys
from pathlib import Path
from src import Downloader, DownloadKind

@click.command(context_settings={"auto_envvar_prefix": "MJDL"})
@click.option('--user_id', '-u', type=str, required=True, help='Your mj user id.')
@click.option('--token', '-t', required=True, type=str, 
	help='Your mj session token (`__Secure-next-auth.session-token` cookie).'
)
@click.option('--kind', '-k', type=click.Choice(['grids', 'upscales', 'all'], case_sensitive=False))
@click.option('--sort-order', '-s', 'sort_oder', show_default=True, type=click.Choice([
	"new", "oldest", "hot", "rising", "top-today", "top-week", "top-month", "top-all", "like_count"
	], case_sensitive=False), default="new", help="Sort order by which to download images."
)
@click.option('--save-models', '-m', 'save_model', is_flag=True, show_default=True, default=False, 
	help="Save the JSON model along with the image."
)
@click.option('--no-date-folders', '-d', 'date_folders', is_flag=True, show_default=True, default=True, 
	help="Save images inside date folders."
)
@click.option('--group-by-day', '-g', 'group_by_month', is_flag=True, show_default=True, default=True, 
	help="Group images by month without creating day folders."
)
@click.option('--skip-low-rated', '-r', 'skip_low_rated', is_flag=True, show_default=True, default=False, 
	help="Skip downloading low-rated images."
)
@click.option('--out', '-o', 'out_path', type=click.Path(path_type=Path), show_default=True, required=False, 
	default=(Path().absolute() / 'jobs'), help='Base path where images are saved.'
)
def cli(user_id: str, kind: str, token: str, sort_oder: str, save_model: bool, date_folders: bool, group_by_month: bool, skip_low_rated: bool, out_path: Path):
	downloader = Downloader(user_id, token)
	download_kind = DownloadKind[kind]
	click.echo("Starting download...")
	downloader.download(download_kind, sort_oder, save_model, out_path, date_folders, group_by_month, skip_low_rated)

if __name__ == "__main__":
	sys.exit(cli())