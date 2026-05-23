# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
* `api.get_currencies()` no longer crashes for user-defined currencies that don't carry an
  ISO-4217 code. `Currency.currency_code` is now `str | None` (default `None`).
* `xmlmap_to_model()` honours `attrs` field defaults in strict mode — missing/empty XML values
  for fields with an explicit default no longer raise `ValueError`.

### Changed
* Python compatibility widened to `>=3.10, <3.14` (was `>=3.10, <=3.11`). Added 3.12 / 3.13 to
  classifiers. The package has been used in production on 3.13 with the previous constraint
  bypassed via `pip install --ignore-requires-python`; this change makes that unnecessary.

## [0.2.0] - 2022-11-12

### Added
* Added timeout options to API class

### Changed
* Some under the hood changes for the repo (src layout, testing)

## [0.1.0] - 2022-08-20

### Added

* Almost full coverage of "get" methods with better English naming for params & types
* Typed data model
