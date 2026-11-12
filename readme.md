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

      - uses: KRST-Kerstin/codesys4-setup@v1

      - name: Check installation
        run: c4-cli version
```

Pin a specific version:

```yaml
      - uses: KRST-Kerstin/codesys4-setup@v1
        with:
          version: "1.0.0.0"
```

For supply-chain safety, pin the action itself to a full commit SHA instead of a tag.

## Inputs

| Name | Required | Default | Description |
| --- | --- | --- | --- |
| `version` | no | `1.0.0.0` | Version explicitly pinned by the reviewed release manifest; other versions fail. |
| `deb-url` | no | reviewed manifest URL | Optional assertion; if set, must exactly match the reviewed manifest URL. |
| `sha256` | no | reviewed manifest pin | Optional assertion; if set, must exactly match the reviewed manifest SHA-256. |
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
      - uses: KRST-Kerstin/codesys4-setup@v1
```

## How it works

1. Checks the runner (Linux, X64, apt/dpkg present).
2. Restores the cached `.deb` (if `cache` is enabled).
3. Downloads the package directly from the CODESYS download server.
4. Verifies the SHA-256 (see below).
5. Installs it with `apt-get install`, so package dependencies are resolved by apt.
6. Reads the installed version with `c4-cli version`.

No CODESYS binaries are stored in this repository. The package is always downloaded from CODESYS at run time.

## Reviewed release manifest and integrity

The action accepts only the manually reviewed release in `releases/codesys4-linux-amd64.json`. That record binds version `1.0.0.0`, Linux `amd64`, DEB format, the exact artifact URL, SHA-256, artifact scope, provenance, and review date. The SHA-256 is a user-approved, locally computed TOFU integrity pin for those exact bytes; it is **not vendor-authenticated** and does not establish CODESYS publisher authenticity. No official checksum, stable channel, feed, or future URL is asserted.

The manifest validator runs before download and installation. Missing or malformed fields, another version/platform/URL/pin, or conflicting overrides fail closed. A cached package is hashed before installation too; a mismatch cannot proceed to `apt-get install`. New releases require a separately reviewed manifest change and corresponding integrity pin; there is no Store scraping or automatic promotion.

```yaml
      - uses: KRST-Kerstin/codesys4-setup@v1
        with:
          version: "1.0.0.0"
```

Optional `deb-url` and `sha256` inputs may only repeat the exact URL and pin already approved in that manifest; they cannot add an unreviewed release.

## Licensing

CODESYS is a product of CODESYS Group and is subject to its own license terms. By using this action you are responsible for complying with them, including terms that apply to automated downloads and to the use of CODESYS in CI. Do not publish container images or artifacts that contain CODESYS binaries to public registries unless the license allows it. The license of this repository covers the action code only.

## Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| `Unsupported OS` / `Unsupported architecture` | Runner is not Linux X64. |
| `apt-get/dpkg not found` | Runner is not Debian-based (for example Alpine). |
| `SHA-256 mismatch` | The artifact bytes do not match the reviewed local TOFU pin; the action stops before installation. |
| Download fails with an HTTP error | The exact URL in the reviewed manifest is unavailable from the runner; `deb-url` cannot select an unreviewed source. |
| Dependency errors during install | Package dependencies differ between distributions. Try the `debian:13` container variant. |

## Maintainers: proposing a new version

1. Verify the exact artifact and establish the proposed SHA-256 pin and its provenance outside this repository.
2. Do not infer a URL, channel, publisher-authenticated checksum, or release from Store HTML.
3. Submit a manual change to the release manifest with version, platform, exact URL, SHA-256 provenance, artifact scope, and review date.
4. Update validator rules and fixture-only tests to review the new pin; do not publish or promote automatically.
5. Keep binary-download integration tests disabled until applicable license/Store terms are confirmed.

## License

MIT for the action code (see `LICENSE`). This does not cover CODESYS software.
