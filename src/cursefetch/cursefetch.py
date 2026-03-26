import json
import os
from typing import Literal

import requests


def get_version_list(project_id: str) -> list:
    """
    Fetches the list of all versions for a given CurseForge project ID.
    :param project_id: The ID of the CurseForge project to fetch versions for.
    :return: A list of version information.
    """
    PER_REQUEST_COUNT = 50
    url = f"https://api.curseforge.com/v1/mods/{project_id}/files?pageSize={PER_REQUEST_COUNT}"

    api_key = os.getenv("CF_API_KEY")
    if api_key is None:
        raise ValueError("CF_API_KEY environment variable is not set.")

    all = []
    try:
        resp = requests.get(url, headers={"X-API-KEY": api_key})
        resp.raise_for_status()
        data = resp.json()
        if "data" in data and len(data["data"]) > 0:
            all.extend(data["data"])
        else:
            raise ValueError("Unable to find any files for the given project ID.")
        while "pagination" in data and len(all) < data["pagination"]["totalCount"]:
            # fetch all pages until we have all the data
            resp = requests.get(
                f"{url}&index={data['pagination']['index'] + PER_REQUEST_COUNT}",
                headers={"X-API-KEY": api_key},
            )
            resp.raise_for_status()
            data = resp.json()
            all.extend(data["data"])
        return all
    except requests.RequestException as e:
        print(f"Error fetching data from CurseForge API: {e}")
        raise
    except (KeyError, IndexError) as e:
        print(f"Error parsing data from CurseForge API: {e}")
        raise


def select_latest_version(
    version_list: list,
    release_type: Literal["release", "beta", "alpha", 1, 2, 3] | None = None,
    order_by: Literal["default", "semver"] = "default",
) -> dict:
    """
    Select the latest version from a list of versions, optionally filtering by release type and ordering by semver.
    :param version_list: The list of versions to select from.
    :param release_type: The release type to filter by (release, beta, alpha, or their corresponding integers).
    :param order_by: The method to order versions by (default or semver).
    :return: The latest version information.
    """

    # convert releaseType to int if it's a string
    if isinstance(release_type, str):
        release_type = {"release": 1, "beta": 2, "alpha": 3}[release_type]
    release_type: int  # hint type

    # filter the list by releaseType if it's not None
    if release_type is not None:
        version_list = [v for v in version_list if v["releaseType"] == release_type]
        if len(version_list) == 0:
            raise ValueError("No versions found for the given release type.")

    if order_by == "semver":
        from packaging.version import InvalidVersion, Version

        try:
            return max(version_list, key=lambda v: Version(v["displayName"]))
        except InvalidVersion:
            # there's a version that doesn't follow semver, so we can't sort by semver
            # FIXME: However, we used a package that may not fully support semver, so find a workaround when someone needs.
            raise
    else:
        # curseforge responds with a upload-order sorted list, so the first item is the latest version
        return version_list[0]
