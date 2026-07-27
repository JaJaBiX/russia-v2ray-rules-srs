# russia-v2ray-rules-srs

This repository republishes Russia routing data from the runetfreedom geo
projects and converts the generated `geoip.dat` and `geosite.dat` files into
sing-box `.srs` rule sets.

The workflow runs every six hours and publishes:

- GitHub Release assets:
  - `geoip.dat`
  - `geoip.dat.sha256sum`
  - `geosite.dat`
  - `geosite.dat.sha256sum`
  - `sing-box.zip`
  - `index.html`
  - `files.json`
- The `release` branch, suitable for `raw.githubusercontent.com` URLs.
- GitHub Pages, including all `.dat`, `.sha256sum`, `.zip`, `.json`, and `.srs`
  files plus a generated index page.

## URLs

Raw branch examples:

- `https://raw.githubusercontent.com/JaJaBiX/russia-v2ray-rules-srs/release/geoip.dat`
- `https://raw.githubusercontent.com/JaJaBiX/russia-v2ray-rules-srs/release/geosite.dat`
- `https://raw.githubusercontent.com/JaJaBiX/russia-v2ray-rules-srs/release/sing-box/rule-set-geosite/geosite-ru-blocked.srs`

GitHub Pages index:

- `https://jajabix.github.io/russia-v2ray-rules-srs/`

## Sources

- `geoip.dat`: `runetfreedom/russia-blocked-geoip`
- `geosite.dat`: `runetfreedom/russia-blocked-geosite`
- `.srs` conversion: `runetfreedom/geodat2srs`
