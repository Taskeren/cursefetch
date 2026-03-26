import argparse
import json
import os
import sys
import traceback
from typing import Literal

from packaging.version import InvalidVersion

import cursefetch.cursefetch as cf
from cursefetch.datastruct import File

from . import download


def main() -> None:
    print("Hello from CurseFetch!")

    argparser = argparse.ArgumentParser(
        description="Fetch the latest version of a CurseForge project."
    )
    argparser.add_argument("project_id", help="The ID of the CurseForge project.")
    argparser.add_argument(
        "--api-key",
        help="The CurseForge API key to use (can also be set via CF_API_KEY environment variable).",
    )
    subparsers = argparser.add_subparsers(dest="command")

    # list versions
    list_parser = subparsers.add_parser(
        "list-version", help="List the versions of the project."
    )
    list_parser.add_argument(
        "-d",
        "--details",
        help="Show detailed information about each version (in JSON format).",
        action="store_true",
    )

    # download version
    download_parser = subparsers.add_parser(
        "download", help="Download a specific version of the project."
    )
    download_parser.add_argument(
        "version",
        help="The version name or id to download (default: latest).",
        default="latest",
    )
    download_parser.add_argument("--simulate-version-selection", action="store_true")
    download_parser.add_argument(
        "-t",
        "--release-type",
        help="The release type to filter by. (default: none). (only applicable when version is 'latest')",
        choices=["release", "beta", "alpha"],
        default=None,
    )
    download_parser.add_argument(
        "--version-order",
        help="The method to order versions by when selecting the latest version. (default: default)",
        choices=["default", "semver"],
        default="default",
    )
    download_parser.add_argument(
        "-o", "--output", help="The path of the output file/directory."
    )
    download_parser.add_argument(
        "-u",
        "--uncompress",
        help="Uncompress the downloaded file to the output directory.",
        action="store_true",
    )

    args = argparser.parse_args()

    # setup API key from argument or environment variable
    if args.api_key:
        print("Using API key from command line argument.")
        os.environ["CF_API_KEY"] = args.api_key

    if args.command == "list-version":
        _command_list_version(args)
    elif args.command == "download":
        _command_download(args)
    else:
        argparser.print_help()


def _command_list_version(args):
    try:
        list = cf.get_version_list(args.project_id)
        if args.details:
            print(json.dumps(list, indent=2))
        else:
            _print_version_list_simple(list)
    except Exception as e:
        print("Failed to fetch version list.")
        traceback.print_exception(e)


def _print_version_list_simple(version_list: list[File]) -> None:
    # calculate the maximum length of the id, name, and release type fields for formatting
    id_max_length = max(len(str(v.id)) for v in version_list)
    name_max_length = max(len(v.displayName) for v in version_list)
    file_date_max_length = max(len(str(v.fileDate)) for v in version_list)

    def release_type_to_str(
        release_type: int | str, dict={1: "release", 2: "beta", 3: "alpha"}
    ) -> str:
        if isinstance(release_type, int):
            return dict.get(release_type, "unknown")
        return release_type

    for v in version_list:
        id = str(v.id).rjust(id_max_length)
        name = str(v.displayName).ljust(name_max_length)
        release_type = release_type_to_str(v.releaseType)
        # the length of "release" and "unknown" is 7
        release_type = release_type.rjust(7)
        file_date = str(v.fileDate).ljust(file_date_max_length)
        print(f"({id})  {name}  {release_type}  {file_date}")


def _command_download(args):
    try:
        version_info: File | None = None
        try:
            version_info = get_project_file(
                args.project_id, args.version, args.release_type, args.version_order
            )
        except ValueError as e:
            sys.exit(str(e))

        if args.simulate_version_selection:
            print("Selected version")
            _print_version_list_simple([version_info])
            return

        # show the selected version info
        print(f"Version: {version_info.displayName} (id: {version_info.id})")
        download_project_file(version_info, args.output, args.uncompress)
    except Exception as e:
        print("Failed to download the version.")
        traceback.print_exception(e)


def get_project_file(
    project_id: str,
    version: str,
    release_type: Literal["release", "beta", "alpha"],
    order_by: Literal["default", "semver"],
) -> File:
    version_list = None
    try:
        version_list = cf.get_version_list(project_id)
    except:
        raise ValueError("Failed to fetch the version list for the given project ID.")

    version_info: File | None = None
    if version == "latest":
        # handle latest version selection
        try:
            version_info = cf.select_latest_version(
                version_list, release_type, order_by
            )
        except InvalidVersion as e:
            raise ValueError(
                "The project contains versions that do not follow semantic versioning (SemVer), and cannot order by semver."
            )
        except:
            raise ValueError("Failed to select the latest version.")
    else:
        # or find the version by name or id
        for version in version_list:
            if version.displayName == version or str(version.id) == version:
                version_info = version
                break

    # fast fail if we couldn't find the version
    if version_info is None:
        raise ValueError("Failed to find a version matching the specified criteria.")

    return version_info


def download_project_file(version_info: File, output_path: str, uncompress: bool):
    # make sure the output path is valid
    if output_path is None:
        output_path = version_info.fileName

    # the path where the downloaded file will be saved
    # if uncompress = true, we will first download to a temporary file and then uncompress it to the output directory
    download_path = output_path if not uncompress else "temp_download.zip"
    try:
        download.download_url(version_info.downloadUrl, download_path)
    except:
        raise ValueError("Failed to download the version.")

    # uncompress the file if requested
    if uncompress:
        try:
            download.uncompress_zip(download_path, output_path)
        except:
            raise ValueError("Failed to uncompress the downloaded file.")
