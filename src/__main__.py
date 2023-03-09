#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import click
import sys
from src import Downloader, DownloadKind


@click.command()
@click.option('--user_id', '-u', type=str, required=True, help='Your mj user id.')
@click.option('--token', '-t', type=str, required=True, help='Your mj session token (`__Secure-next-auth.session-token` cookie).')
@click.option('--kind', '-k', type=click.Choice(['grids', 'upscales', 'all'], case_sensitive=False))
@click.option('--order', '-o', type=click.Choice(["new", "oldest", "hot", "rising", "top-today", "top-week", "top-month", "top-all", "like_count"], case_sensitive=False), default="new")
def cli(user_id: str, kind: str, token: str, order: str):
	downloader = Downloader(user_id, token)
	download_kind = DownloadKind[kind]
	click.echo("Starting download...")
	downloader.download(download_kind, order, True, True, False)

if __name__ == "__main__":
	sys.exit(cli())