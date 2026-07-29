# Changelog

## [0.2.1](https://github.com/DOFER998/aioplatega/compare/v0.2.0...v0.2.1) (2026-07-29)


### Bug Fixes

* keep uv.lock in step with the released version ([d6cc2c7](https://github.com/DOFER998/aioplatega/commit/d6cc2c7f1d0730c179cd472478e50dfe00cf5cbb))
* publish from the entry workflow, not a reusable one ([3f1586e](https://github.com/DOFER998/aioplatega/commit/3f1586e578a1bc4f85a9d2f11962c96f51d3c5a5))

## [0.2.0](https://github.com/DOFER998/aioplatega/compare/v0.1.0...v0.2.0) (2026-07-29)


### Features

* cover the documented Platega API surface ([016f6eb](https://github.com/DOFER998/aioplatega/commit/016f6eb02ad8608959c64f8233ad5d17e8330dc5))
* type the nested shapes the specs document ([eeff8ba](https://github.com/DOFER998/aioplatega/commit/eeff8ba418cda52c6dafc5d5a53379ae71885ea1))
* verify incoming callbacks, in constant time ([ab45479](https://github.com/DOFER998/aioplatega/commit/ab45479b979f375812f27f088ee5f987cdaff297))


### Bug Fixes

* accept the statuses the API actually returns ([ef58c40](https://github.com/DOFER998/aioplatega/commit/ef58c404592037cf656dbd2e9ae56a65656fb01c))
* correct request construction and tighten the error contract ([bf2fc79](https://github.com/DOFER998/aioplatega/commit/bf2fc79af8df58807c17139a26f52db5963b1b56))
* correct the stale conversions example, and guard against the next one ([801f605](https://github.com/DOFER998/aioplatega/commit/801f6055081c84162f6ecc0bce2ffed129b5f140))
* model the responses the API actually returns ([eb33031](https://github.com/DOFER998/aioplatega/commit/eb3303125250e7ea1fee9b59bc7ff887bf8dcbf1))
* send the required subscription charge interval ([9bd3699](https://github.com/DOFER998/aioplatega/commit/9bd3699f5903ca87c49f43e5d79b825f7cf584a6))
* stop treating PaymentMethodInt as the set of valid methods ([f4b188f](https://github.com/DOFER998/aioplatega/commit/f4b188fcf9d8b4fce3e65610cfd3a7d504463ff1))


### Documentation

* drop aiogram references from user-facing copy ([98006b0](https://github.com/DOFER998/aioplatega/commit/98006b0a3ba149b98152efe049fa6e1051ec6959))
* record the operational rules the official docs state in prose ([1b06254](https://github.com/DOFER998/aioplatega/commit/1b06254a7861e4c18c047537a8339ce423987cf0))
* replace inline comments with Google-style docstrings ([e2778c7](https://github.com/DOFER998/aioplatega/commit/e2778c7fc718df029d1ac1f7323d51ca4ea3446b))
* rewrite the README as markdown ([3be638c](https://github.com/DOFER998/aioplatega/commit/3be638cb5fc74670bd1d959345140aa9e10cf179))
* verify against the published OpenAPI, not the rendered pages ([39ec072](https://github.com/DOFER998/aioplatega/commit/39ec072baf311d0d4f9eb2fc451e11a06d2ce64e))
