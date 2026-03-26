import argparse
import json
import os
import sys
import traceback

from packaging.version import InvalidVersion

import cursefetch.cursefetch as cf

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
        command_list_version(args)
    elif args.command == "download":
        command_download(args)
    else:
        argparser.print_help()


def command_list_version(args):
    try:
        list = cf.get_version_list(args.project_id)
        if args.details:
            print(json.dumps(list, indent=2))
        else:
            print_version_list_simple(list)
    except Exception as e:
        print("Failed to fetch version list.")
        traceback.print_exception(e)


def print_version_list_simple(version_list: list) -> None:
    # calculate the maximum length of the id, name, and release type fields for formatting
    id_max_length = max(len(str(v["id"])) for v in version_list)
    name_max_length = max(len(v["displayName"]) for v in version_list)
    file_date_max_length = max(len(str(v["fileDate"])) for v in version_list)

    def release_type_to_str(
        release_type: int | str, dict={1: "release", 2: "beta", 3: "alpha"}
    ) -> str:
        if isinstance(release_type, int):
            return dict.get(release_type, "unknown")
        return release_type

    for v in version_list:
        id = str(v["id"]).rjust(id_max_length)
        name = str(v["displayName"]).ljust(name_max_length)
        release_type = release_type_to_str(v["releaseType"])
        # the length of "release" and "unknown" is 7
        release_type = release_type.rjust(7)
        file_date = str(v["fileDate"]).ljust(file_date_max_length)
        print(f"({id})  {name}  {release_type}  {file_date}")


def command_download(args):
    try:
        version = args.version
        # the selected version info dict
        version_info = None

        # grab the version list
        list = None
        try:
            list = cf.get_version_list(args.project_id)
        except:
            sys.exit("Failed to fetch the version list for the given project ID.")

        if version == "latest":
            # handle latest version selection
            try:
                version_info = cf.select_latest_version(
                    list, release_type=args.release_type, order_by=args.version_order
                )
            except InvalidVersion as e:
                sys.exit(
                    "The project contains versions that do not follow semantic versioning (SemVer), and cannot order by semver."
                )
            except:
                sys.exit("Failed to select the latest version.")
        else:
            # or find the version by name or id
            for v in list:
                if v["displayName"] == version or str(v["id"]) == version:
                    version_info = v
                    break

        # fast fail if we couldn't find the version
        if version_info is None:
            sys.exit("Failed to find a version matching the specified criteria.")

        # dump simulation info and return
        if args.simulate_version_selection:
            print("Selected version")
            print_version_list_simple([version_info])
            return

        # show the selected version info
        print(f"Version: {version_info['displayName']} (id: {version_info['id']})")

        # download the file
        output_path = args.output if not args.uncompress else "temp_download.zip"
        try:
            download.download_url(version_info["downloadUrl"], output_path)
        except:
            sys.exit("Failed to download the version.")

        # uncompress the file if requested
        if args.uncompress:
            try:
                download.uncompress_zip(output_path, args.output)
            except:
                sys.exit("Failed to uncompress the downloaded file.")

    except Exception as e:
        print("Failed to download the version.")
        traceback.print_exception(e)
