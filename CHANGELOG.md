# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-07-19

### Added
* Add support for Python 3.12, 3.13, and 3.14

### Changed
* Migrate project packaging and dependency management from Poetry to uv
* Replace Black, isort, flake8, and tox with Ruff and direct uv commands

### Fixed
* Ignore folder objects returned by `getPlaceList` when retrieving accounts

## [0.2.0] - 2022-11-12

### Added
* Added timeout options to API class

### Changed
* Some under the hood changes for the repo (src layout, testing)

## [0.1.0] - 2022-08-20

### Added

* Almost full coverage of "get" methods with better English naming for params & types
* Typed data model
