# Changelog

## 0.1.0 (2025-11-30)


### Features

* add critical live game data types from TypeScript ([278b5f1](https://github.com/wooto/lol-replay-recorder-py/commit/278b5f1cedae9eb15452b219194a052f9a8d3d8f))
* add critical missing utils functions for Riot API integration ([758a6c9](https://github.com/wooto/lol-replay-recorder-py/commit/758a6c96d1c35e96a011e8f815fa32d7583047ee))
* add CustomError exception class ([f83df6a](https://github.com/wooto/lol-replay-recorder-py/commit/f83df6a5a3f3f254f6e0361f7b51f67b2acec0f3))
* add GitHub Actions CI workflow ([a679908](https://github.com/wooto/lol-replay-recorder-py/commit/a6799081b4b56dd1ec9b023a43e07bbdcb10bd93))
* add IniEditor for managing INI config files ([dc93a5d](https://github.com/wooto/lol-replay-recorder-py/commit/dc93a5dff4966defb33d6ac0953be739d8ab7503))
* add LeagueClient main orchestrator controller ([86963bc](https://github.com/wooto/lol-replay-recorder-py/commit/86963bc2108de2f65be884071386d180173cf08a))
* add LeagueReplayClient for replay API control ([08b453a](https://github.com/wooto/lol-replay-recorder-py/commit/08b453ad70e549852a376c198a853707b5ae0d04))
* add Locale enum with all supported LoL locales ([d6a6649](https://github.com/wooto/lol-replay-recorder-py/commit/d6a66498095192e85ba64e1963cf314af6f5c5e1))
* add make_lcu_request for League Client API with lockfile auth ([e988122](https://github.com/wooto/lol-replay-recorder-py/commit/e988122167aa2ee4bf25b056cf91e68d803f703b))
* add PyPI distribution setup ([#5](https://github.com/wooto/lol-replay-recorder-py/issues/5)) ([ca93f78](https://github.com/wooto/lol-replay-recorder-py/commit/ca93f7842c5acebe95b6bc6900d74eeb59c5b439))
* add replay type definitions for recording and rendering ([ee58f56](https://github.com/wooto/lol-replay-recorder-py/commit/ee58f5641316c243341abb8b7d78106cb9dcdc98))
* add Riot platform IDs and region types ([5aae966](https://github.com/wooto/lol-replay-recorder-py/commit/5aae9664508a23a460369c2639d5a37476799780))
* add RiotGameClient controller for game client process management ([7b0d75e](https://github.com/wooto/lol-replay-recorder-py/commit/7b0d75e53d863cb8bc09c3a405ccdd180ca7e1c8))
* add Summoner model with riot ID generation ([eb0fdc1](https://github.com/wooto/lol-replay-recorder-py/commit/eb0fdc11f8eb77181ee94826a8a7c6ac36bd9cb8))
* add utility functions module with sleep and conversion helpers ([12f680e](https://github.com/wooto/lol-replay-recorder-py/commit/12f680e2d3bf8a768120e71d3b18d7085061fdbc))
* add WindowHandler for keyboard/mouse automation with pyautogui ([33b17bb](https://github.com/wooto/lol-replay-recorder-py/commit/33b17bbdc8736e47db7772a6e47ffaa7dfc90c8b))
* add YamlEditor for managing YAML config files ([0789f9d](https://github.com/wooto/lol-replay-recorder-py/commit/0789f9d3ab9235d36434e57e733394a0ddfe00d8))
* implement LeagueClientUx controller with comprehensive test coverage ([4d2ed0e](https://github.com/wooto/lol-replay-recorder-py/commit/4d2ed0e02d179d8e1fa6eaeff68b416af45932a2))
* implement PlayerInfo structure matching TypeScript Metadata.ts ([1ee5908](https://github.com/wooto/lol-replay-recorder-py/commit/1ee5908b8b6be7ca931ac06815f7ee2fef1164f5))
* migrate from Poetry to uv for modern Python tooling ([4efa406](https://github.com/wooto/lol-replay-recorder-py/commit/4efa406736b8fc59a7853d5666c77d13dd938867))
* migrate from Poetry to uv for modern Python tooling ([4efa406](https://github.com/wooto/lol-replay-recorder-py/commit/4efa406736b8fc59a7853d5666c77d13dd938867))


### Bug Fixes

* add pygetwindow as dev dependency and update test assertions ([060db39](https://github.com/wooto/lol-replay-recorder-py/commit/060db3958d5590c58fcc5a30e5ab18f1f2f1c0db))
* add runtime validation for TypedDict types in tests ([57c3d0c](https://github.com/wooto/lol-replay-recorder-py/commit/57c3d0c5e7493f009b2d92d28c9d4c072f99ca7b))
* convert PlatformId values to lowercase to match TypeScript reference ([edf2ee9](https://github.com/wooto/lol-replay-recorder-py/commit/edf2ee92d22511d73af3d56ccfa146d8bb70343a))
* correct summoner test case expectation ([11eb2df](https://github.com/wooto/lol-replay-recorder-py/commit/11eb2df151d906f267b0959fac4acd5f17696f9e))
* import NotRequired from typing_extensions for Python 3.10 compatibility ([1773c48](https://github.com/wooto/lol-replay-recorder-py/commit/1773c488106368dd196d1b0f62b89521995a0067))
* import NotRequired from typing_extensions in replay_type.py ([0e5913e](https://github.com/wooto/lol-replay-recorder-py/commit/0e5913e6890a7b52056c830eb9db9a067007babe))
* replace deprecated tool.uv.dev-dependencies with dependency-groups.dev ([6071911](https://github.com/wooto/lol-replay-recorder-py/commit/60719119b203f7846e5332cd05076f89af2a068b))
* resolve CI test failures after uv migration ([8b302dc](https://github.com/wooto/lol-replay-recorder-py/commit/8b302dc01a4458ab28b934a7d7d7ca135a74439d))
* resolve DISPLAY error in CI by making pyautogui imports lazy ([739297e](https://github.com/wooto/lol-replay-recorder-py/commit/739297ed9cf19bd4dcd61f64dbd43a4ab976554a))
* resolve DISPLAY error in CI by making pyautogui imports lazy ([#1](https://github.com/wooto/lol-replay-recorder-py/issues/1)) ([433ff0a](https://github.com/wooto/lol-replay-recorder-py/commit/433ff0a2c0e60e384e6f26703436b8d8859604a3))
* resolve LCU request test parameter mismatches ([7174c75](https://github.com/wooto/lol-replay-recorder-py/commit/7174c751555b2b05a8f0285bde10bdb66a37d25b))
* resolve mypy type checking failures across codebase ([378bdfa](https://github.com/wooto/lol-replay-recorder-py/commit/378bdfaaaf663b16fd25877a4b795a97b24783a3))
* resolve pygetwindow API compatibility issues in window handler tests ([8fe9479](https://github.com/wooto/lol-replay-recorder-py/commit/8fe94794d55ba07e5177f181455114715d3670a6))
* resolve ruff linting issues and finalize CI fixes ([6830fe6](https://github.com/wooto/lol-replay-recorder-py/commit/6830fe6938982aaa775669e34472b186f70a5045))
* resolve test failures after uv migration ([da71ec6](https://github.com/wooto/lol-replay-recorder-py/commit/da71ec6d99213e116f032d345189e6d5cbf023b3))
* set DISPLAY environment variable for headless CI environments ([3120ee7](https://github.com/wooto/lol-replay-recorder-py/commit/3120ee7a95bfface11014b80d01cc81a4e028341))
* update test patches to use lazy import functions ([80641b6](https://github.com/wooto/lol-replay-recorder-py/commit/80641b63ba3d3945b4f76229253e3d44289aa71a))


### Documentation

* add Python port design and implementation plans ([cc7516d](https://github.com/wooto/lol-replay-recorder-py/commit/cc7516d3c3cf75fc20ca937e63c469f99c37624d))
* add TypeScript reference location to implementation plan ([3854ca3](https://github.com/wooto/lol-replay-recorder-py/commit/3854ca3c052eb60970c125f62e58f95827e0fa38))
* update development commands for uv ([4bf4f4d](https://github.com/wooto/lol-replay-recorder-py/commit/4bf4f4d5dd939a7aff9b960ae1c63a80d9c4b15b))
* update README with installation and usage examples ([#4](https://github.com/wooto/lol-replay-recorder-py/issues/4)) ([9658137](https://github.com/wooto/lol-replay-recorder-py/commit/96581375819ee2fe0c7e03fd3b69a0614d909377))
