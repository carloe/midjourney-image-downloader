import os
import requests
import urllib.request
from datetime import datetime
from enum import Enum
from typing import List, Any, Dict


class DownloadKind(Enum):
    grids = "grids"
    upscales = "upscales"
    all = "all"


class Parameters():
    def __init__(self, download_kind: DownloadKind, order_by: str, date_folders: bool, group_by_month: bool, skip_low_rated: bool):
        self.download_kind = download_kind
        self.date_folders = date_folders
        self.group_by_month = group_by_month
        self.skip_low_rated = skip_low_rated
        self.order_by = order_by


class Downloader(): 
    def __init__(self, user_id: str, session_token: str):
        self._user_id = user_id
        self._user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        self._headers = {'User-Agent': self._user_agent }
        self._cookies = {'__Secure-next-auth.session-token': session_token}

    def download(self, download_kind: DownloadKind, order_by: str, date_folders: bool, group_by_month: bool, skip_low_rated: bool):
        parameters = Parameters(download_kind, order_by, date_folders, group_by_month, skip_low_rated)
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
            if not os.path.isdir(f"jobs/{year}"):
                os.makedirs(f"jobs/{year}")
            if not os.path.isdir(f"jobs/{year}/{month}"):
                os.makedirs(f"jobs/{year}/{month}")
            if parameters.group_by_month:
                if not os.path.isdir(f"jobs/{year}/{month}/{image_id}"):
                    os.makedirs(f"jobs/{year}/{month}/{image_id}")
                return f"jobs/{year}/{month}/{image_id}"
            else:
                if not os.path.isdir(f"jobs/{year}/{month}/{day}"):
                    os.makedirs(f"jobs/{year}/{month}/{day}")
                if not os.path.isdir(f"jobs/{year}/{month}/{day}/{image_id}"):
                    os.makedirs(f"jobs/{year}/{month}/{day}/{image_id}")
                return f"jobs/{year}/{month}/{day}/{image_id}"
        else:
            if not os.path.isdir(f"jobs/{image_id}"):
                os.makedirs(f"jobs/{image_id}")
            return f"jobs/{image_id}"


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
        elif os.path.isfile(f"jobs/{year}/{month}/{image_id}/done") or \
                os.path.isfile(f"jobs/{year}/{month}/{day}/{image_id}/done") or \
                os.path.isfile(f"jobs/{image_id}/done"):
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
            completed_file_path = f"{image_path}/done"
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