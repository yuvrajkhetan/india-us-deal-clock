# India–US Trade Deal Clock

A Doomsday-Clock-style estimate of how close India and the US are to signing the first tranche of their Bilateral Trade Agreement.

Live page: https://yuvrajkhetan.github.io/india-us-deal-clock/

All figures are computed in the browser from the JSON data block in `index.html`. The data is refreshed daily with new dated, sourced inputs.

## Link preview

`og.png`, the share tags and the pre-rendered page content in `index.html` (so crawlers that skip JavaScript still see the readings) are regenerated from the page's own data by `python3 scripts/build_share.py` (needs Playwright). Fonts in `scripts/fonts` are used under the SIL Open Font License.
