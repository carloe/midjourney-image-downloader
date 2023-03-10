import requests
import urllib.request
from datetime import datetime
from enum import Enum
from typing import List, Any, Dict
from pathlib import Path
import json


class DownloadKind(Enum):
    grids = "grids"
    upscales = "upscales"
    all = "all"


class DownloadAggregation(Enum):
    prompt = "prompt"
    month = "month"
    day = "day"


class Parameters():
    def __init__(
        self, 
        download_kind: DownloadKind, 
        order_by: str, 
        aggregate_by: DownloadAggregation,
        save_model: bool, 
        save_prompt: bool,
        save_command: bool,
        out_path: Path, 
        skip_low_rated: bool
    ):
        self.download_kind = download_kind
        self.skip_low_rated = skip_low_rated
        self.order_by = order_by
        self.out_path = out_path
        self.save_model = save_model
        self.save_prompt = save_prompt
        self.save_command = save_command
        self.aggregate_by = aggregate_by


class Downloader(): 
    def __init__(self, user_id: str, session_token: str):
        self._user_id = user_id
        self._user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        self._headers = {'User-Agent': self._user_agent }
        self._cookies = {'__Secure-next-auth.session-token': session_token}

    def download(
        self, 
        download_kind: DownloadKind, 
        order_by: str, 
        aggregate_by: DownloadAggregation,
        save_model: bool, 
        save_prompt: bool,
        save_command: bool,
        out_path: Path, 
        skip_low_rated: bool
    )  -> None:
        page_index = 1
        parameters = Parameters(download_kind, order_by, aggregate_by, save_model, save_prompt, save_command, out_path, skip_low_rated)
        page_data = self._fetch_api_page(parameters, page_index)
        while page_data:
            if isinstance(page_data, list) and len(page_data) > 0 and "no jobs" in page_data[0].get("msg", "").lower():
                print("Reached end of available results")
                break
            print(f"Downloading page #{page_index} (order by '{parameters.order_by}')")
            self._download_page(page_data, parameters)
            page_index += 1
            page_data = self._fetch_api_page(parameters, page_index)           

    def _fetch_api_page(self, parameters: Parameters, page: int) -> List[Dict[str, Any]]:
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


    def _download_page(self, page_json, parameters: Parameters) -> None:
        for idx, image_json in enumerate(page_json):
            filename = self._download_image(image_json, parameters)
            if filename:
                print(f"{idx+1}/{len(page_json)} Downloaded {filename}")

    def _download_image(self, image_json: List[Dict[str, Any]], parameters: Parameters) -> str:
        image_paths = image_json.get("image_paths", [])
        image_id = image_json.get("id")

        enqueue_time_str = image_json.get("enqueue_time")
        enqueue_time = datetime.strptime(enqueue_time_str, "%Y-%m-%d %H:%M:%S.%f")
        year = enqueue_time.year
        month = enqueue_time.month
        day = enqueue_time.day

        filename = self._filename_for(parameters, image_json)
        output_path = self._output_path_for(parameters, image_json)

        ranking_by_user = image_json.get("ranking_by_user")
        if parameters.skip_low_rated and ranking_by_user and isinstance(ranking_by_user, int) and (ranking_by_user in [1, 2]):
            return
        elif self._local_data_exists(output_path, filename):
            print(f"Image {filename}.png exists. Skipping.")
            return
        else:
            try: 
                output_path.mkdir(parents=True, exist_ok=False)
            except FileExistsError:
                pass
            for idx, image_url in enumerate(image_paths):
                if idx > 0:
                    filename = f"{filename}-{idx}"
                full_path = f"{output_path}/{filename}.png"
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent', self._user_agent)]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(image_url, full_path)
            if parameters.save_model is True:
                output_model_path = output_path / "model.json"
                with open(output_model_path, 'w') as outfile:
                    json.dump(image_json, outfile, indent=4)
            if parameters.save_prompt is True:
                prompt = image_json.get("prompt")
                output_prompt_path = output_path / "prompt.txt"
                with open(output_prompt_path, 'w') as f:
                    f.write(prompt)
            if parameters.save_command is True:
                command = image_json.get("full_command")
                output_command_path = output_path / "command.txt"
                with open(output_command_path, 'w') as f:
                    f.write(command)
        return filename

    @staticmethod
    def _local_data_exists(path: Path, filename: str) -> bool:
        full_path = path / f'{filename}.png'
        return full_path.is_file()

    @staticmethod
    def _output_path_for(parameters: Parameters, image_json: List[Dict[str, Any]]) -> Path:
        prompt = image_json.get("prompt")
        enqueue_time_str = image_json.get("enqueue_time")
        enqueue_time = datetime.strptime(enqueue_time_str, "%Y-%m-%d %H:%M:%S.%f")
        year = enqueue_time.year
        month = enqueue_time.month
        day = enqueue_time.day
        match parameters.aggregate_by:
            case DownloadAggregation.prompt:
                sanitized = prompt.replace(" ", "_").replace(",", "").replace("*", "").replace("'", "").replace(":", "").replace(
                    "__", "_").replace("<", "").replace(">", "").replace("/", "").replace(".", "").lower().strip("_*")[:100]
                return parameters.out_path / sanitized
            case DownloadAggregation.month:
                return parameters.out_path / f"{year}/{month}"
            case DownloadAggregation.day:
                return parameters.out_path / f"{year}/{month}/{day}"

    @staticmethod
    def _filename_for(parameters: Parameters, image_json: List[Dict[str, Any]]) -> str:
        if (parameters.aggregate_by == DownloadAggregation.day or parameters.aggregate_by == DownloadAggregation.month):
            prompt = image_json.get("prompt")
            return prompt.replace(" ", "_").replace(",", "").replace("*", "").replace("'", "").replace(":", "").replace(
                "__", "_").replace("<", "").replace(">", "").replace("/", "").replace(".", "").lower().strip("_*")[:97]
        return image_json.get("id")
