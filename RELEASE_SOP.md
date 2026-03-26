# Release Standard Operating Procedures

Just make sure that I will remember how to do this.

Documents: <https://docs.astral.sh/uv/guides/package/#preparing-your-project>

## Building

Use `uv build`, and the output is in `/dist`.

## Versioning

Use `uv version` to get the version, `uv version {newValue}` to update version, or `uv version {newVersion} --dry-run` to inspect what it will be after applying.

Use `uv version --bump minor` to bump the version.
It also supports `major`, `minor`, `patch`, `stable`, `alpha`, `beta`, `rc`, `post`, and `dev` in replacement of `minor`.
And it accepts more than one of them, like `uv version --bump patch --bump dev=66463664`.

## Publishing

Use `uv publish` to publish the package.

Currently, PyPI only accepts authentication via token, so the username is fixed to `__token__`, and the password is the token.

Hint: my token is in the RC file.
