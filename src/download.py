import requests
import urllib.request
from datetime import datetime
from enum import Enum
from typing import List, Any, Dict
from pathlib import Path

class DownloadKind(Enum):
    grids = "grids"
    upscales = "upscales"
    all = "all"


class Parameters():
    def __init__(self, download_kind: DownloadKind, order_by: str, out_path: Path, date_folders: bool, group_by_month: bool, skip_low_rated: bool):
        self.download_kind = download_kind
        self.date_folders = date_folders
        self.group_by_month = group_by_month
        self.skip_low_rated = skip_low_rated
        self.order_by = order_by
        self.out_path = out_path


class Downloader(): 
    def __init__(self, user_id: str, session_token: str):
        self._user_id = user_id
        self._user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        self._headers = {'User-Agent': self._user_agent }
        self._cookies = {'__Secure-next-auth.session-token': session_token}

    def download(self, download_kind: DownloadKind, order_by: str, out_path: Path, date_folders: bool, group_by_month: bool, skip_low_rated: bool):
        parameters = Parameters(download_kind, order_by, out_path, date_folders, group_by_month, skip_low_rated)
        self._paginated_download(parameters)            

    def _get_api_page(self, parameters: Parameters, page: int):
        api_url = "https://www.midjourney.com/api/app/recent-jobs/" \
                  f"?orderBy={parameters.order_by}&jobStatus=completed&userId={self._user_id}" \
                  f"&dedupe=true&refreshApi=0&amount=50&page={page}"

        match parameters.download_kind:
            case DownloadKind.upscales:
                api_url += "&jobType=upscale"
            case DownloadKind.grids:
                api_url += "&jobType=grid"
            case DownloadKind.all:
                pass

        try: 
            response = requests.get(api_url, cookies=self._cookies, headers=self._headers)
            result = response.json()
            return result
        except requests.exceptions.RequestException as e:
            print(f'HTTP Request failed: {e}')


    def _download_page(self, page_json, parameters: Parameters):
        for idx, image_json in enumerate(page_json):
            filename = self._save_prompt(image_json, parameters)
            if filename:
                print(f"{idx+1}/{len(page_json)} Downloaded {filename}")


    def _ensure_path_exists(self, year, month, day, image_id, parameters: Parameters):
        if parameters.date_folders:
            if parameters.group_by_month:
                date_path = parameters.out_path / f"{year}/{month}/{image_id}"
                try: 
                    date_path.mkdir(parents=True, exist_ok=False)
                except FileExistsError:
                    pass
                return date_path
            else:
                date_path = parameters.out_path / f"{year}/{month}/{day}/{image_id}"
                try: 
                    date_path.mkdir(parents=True, exist_ok=False)
                except FileExistsError:
                    pass
                return date_path
        else:
            image_path = parameters.out_path / f"{image_id}"
            try: 
                image_path.mkdir(parents=True, exist_ok=False)
            except FileExistsError:
                pass
            return image_path

    def _save_prompt(self, image_json: List[Dict[str, Any]], parameters: Parameters):
        image_paths = image_json.get("image_paths", [])
        image_id = image_json.get("id")
        prompt = image_json.get("prompt")
        enqueue_time_str = image_json.get("enqueue_time")
        enqueue_time = datetime.strptime(enqueue_time_str, "%Y-%m-%d %H:%M:%S.%f")
        year = enqueue_time.year
        month = enqueue_time.month
        day = enqueue_time.day

        filename = prompt.replace(" ", "_").replace(",", "").replace("*", "").replace("'", "").replace(":", "").replace(
            "__", "_").replace("<", "").replace(">", "").replace("/", "").replace(".", "").lower().strip("_*")[:100]

        ranking_by_user = image_json.get("ranking_by_user")
        if parameters.skip_low_rated and ranking_by_user and isinstance(ranking_by_user, int) and (ranking_by_user in [1, 2]):
            return
        elif Path(f"{year}/{month}/{image_id}/done").is_file() or \
                Path(f"{year}/{month}/{day}/{image_id}/done").is_file() or \
                Path(f"{image_id}/done").is_file():
            return
        else:
            image_path = self._ensure_path_exists(year, month, day, image_id, parameters)
            full_path = f"{image_path}/{filename}.png"
            for idx, image_url in enumerate(image_paths):
                if idx > 0:
                    filename = f"{filename[:97]}-{idx}"
                    full_path = f"{image_path}/{filename}.png"
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent', self._user_agent)]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(image_url, full_path)
            completed_file_path = image_path / "done"
            if completed_file_path.is_file():
                print("File already downloaded... skipping.")
            else:
                f = open(completed_file_path, "x")
                f.close()
        return full_path


    def _paginated_download(self, parameters: Parameters):
        page = 1
        page_of_results = self._get_api_page(parameters, page)
        while page_of_results:
            if isinstance(page_of_results, list) and len(page_of_results) > 0 and "no jobs" in page_of_results[0].get("msg", "").lower():
                print("Reached end of available results")
                break

            print(f"Downloading page #{page} (order by '{parameters.order_by}')")
            self._download_page(page_of_results, parameters)
            page += 1
            page_of_results = self._get_api_page(parameters, page)