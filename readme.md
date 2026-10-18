# Setup CODESYS 4

A GitHub Action that installs [CODESYS 4](https://content.helpme-codesys.com/en/CODESYS%204/_c4_start_page.html) on a Linux runner, so later steps of your workflow can build and process CODESYS 4 projects.

> **Unofficial.** This project is not affiliated with or endorsed by CODESYS Group.

## Usage

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: KRST-Kerstin/setup-codesys4@v1

      - name: Check installation
        run: c4-cli version
```

Pin a specific version:

```yaml
      - uses: KRST-Kerstin/setup-codesys4@v1
        with:
          version: "1.0.0.0"
```

For supply-chain safety, pin the action itself to a full commit SHA instead of a tag.

## Inputs

| Name | Required | Default | Description |
| --- | --- | --- | --- |
| `version` | no | `1.0.0.0` | CODESYS 4 version to install. |
| `deb-url` | no | derived from `version` | Override the download URL of the `.deb` package. |
| `sha256` | no | built-in value for known versions | Expected SHA-256 of the package. Overrides the built-in value. |
| `cache` | no | `true` | Cache the downloaded `.deb` between runs. |

## Outputs

| Name | Description |
| --- | --- |
| `version` | Output of `c4-cli version` after installation. |

## Requirements

- Linux runner, X64 (amd64) architecture
- Debian-based system with `apt-get` and `dpkg`
- `sudo` (available on GitHub-hosted runners)
- Network access to the CODESYS download server

The action fails early with a clear error when one of these is not met.

Tested on: `ubuntu-22.04`, `ubuntu-24.04`. To run on Debian, use a job container:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    container: debian:13
    steps:
      - run: apt-get update && apt-get install -y --no-install-recommends ca-certificates curl sudo
      - uses: KRST-Kerstin/setup-codesys4@v1
```

## How it works

1. Checks the runner (Linux, X64, apt/dpkg present).
2. Restores the cached `.deb` (if `cache` is enabled).
3. Downloads the package directly from the CODESYS download server.
4. Verifies the SHA-256 (see below).
5. Installs it with `apt-get install`, so package dependencies are resolved by apt.
6. Reads the installed version with `c4-cli version`.

No CODESYS binaries are stored in this repository. The package is always downloaded from CODESYS at run time.

## Integrity check

If a SHA-256 is known for the selected `version` (built into the action) or passed via `sha256`, the download is verified and the step fails on a mismatch. If no expected value exists, the action only checks that the file is a valid `.deb`, prints a warning, and logs the computed SHA-256 so you can pin it:

```yaml
      - uses: KRST-Kerstin/setup-codesys4@v1
        with:
          version: "1.0.0.0"
          sha256: "<value from the log>"
```

## Licensing

CODESYS is a product of CODESYS Group and is subject to its own license terms. By using this action you are responsible for complying with them, including terms that apply to automated downloads and to the use of CODESYS in CI. Do not publish container images or artifacts that contain CODESYS binaries to public registries unless the license allows it. The license of this repository covers the action code only.

## Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| `Unsupported OS` / `Unsupported architecture` | Runner is not Linux X64. |
| `apt-get/dpkg not found` | Runner is not Debian-based (for example Alpine). |
| `SHA-256 mismatch` | The file at the URL changed, the download was corrupted, or the built-in hash is outdated. Check the logged hash. |
| Download fails with an HTTP error | The URL changed or the server is unavailable from the runner network. Try `deb-url`, or cache the file. |
| Dependency errors during install | Package dependencies differ between distributions. Try the `debian:13` container variant. |

## Maintainers: adding a new version

1. Download the package from the official CODESYS source.
2. Compute its hash: `sha256sum codesys-4_<version>_amd64.deb`.
3. Add the version and hash to the `KNOWN` table in `action.yml`.
4. Run the test workflow on all supported runners.
5. Tag a release and move the major tag (`v1`).

## License

MIT for the action code (see `LICENSE`). This does not cover CODESYS software.
