import os
import zipfile

import requests
from tqdm import tqdm


def download_url(url: str, destination: str):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get("Content-Length", 0))
        with (
            open(destination, "wb") as f,
            # use tqdm to show a progress bar while downloading
            tqdm(
                desc=f"Downloading {destination}",
                total=total_size,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar,
        ):
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    size = f.write(chunk)
                    bar.update(size)


def uncompress_zip(zip_path: str, destination: str):
    # ensure the destination directory exists
    if not os.path.exists(destination):
        os.makedirs(destination)

    with zipfile.ZipFile(zip_path, "r") as zip_:
        # calculate the total size of the files in the zip for progress tracking
        total_size = sum(file.file_size for file in zip_.infolist())
        with tqdm(
            total=total_size,
            unit = "B",
            unit_scale=True,
            desc=f"Uncompressing {zip_path}",
        ) as bar:
            for file in zip_.infolist():
                # construct the full path for the extracted file
                target_path = os.path.join(destination, file.filename)
                # ensure the target directory exists
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                # skip directories, zipfile will create them automatically when extracting files
                if file.is_dir():
                    continue
                # read and write the file in chunks to show progress
                with zip_.open(file) as source, open(target_path, "wb") as target:
                    while True:
                        chunk = source.read(64 * 1024)
                        if not chunk:
                            break
                        target.write(chunk)
                        bar.update(len(chunk))
