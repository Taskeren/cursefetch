# CurseFetch

Yet another tool to fetch files from CurseForge.

## Usage

#### Global Optional Parameters

- `--api-key`: set the CurseForge API key.

The API Key must present in either Environment Variables (`CF_API_KEY`) or in the parameters!

See [About the CurseForge API and How to Apply for a Key](https://support.curseforge.com/support/solutions/articles/9000208346-about-the-curseforge-api-and-how-to-apply-for-a-key) to apply for a key.

### List available versions

Using `cursefetch {project_id} list-version` to list the available versions.

#### Optional Parameters

- `-d` or `--details`: print full JSON response instead of pretty printing the versions.

### Download files

Using `cursefetch {project_id} download {version}` to download the files.

The version parameter can be `latest`.

#### Optional Parameters

- `-t` or `--release-type`: specify the release type when searching for a _latest_ version.
- `--version-order`: the method to order the versions, either `default` or `semver`.
- `-o` or `--output`: the path to the file or directory of output; if `--uncompress` is enabled, the file will always be downloaded to `temp_download.zip`, and this parameter is used for the path to decompressed files.
- `-u` or `--uncompress`: uncompress the downloaded *zip* file.
