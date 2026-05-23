# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
* `api.set_record_list(records)` — first write method on the API. Accepts a list of dicts with
  the keys documented in WSDL (`server_id`/`client_id`, `place_id`, `budget_object_id`, `sum`,
  `operation_date`, `comment`, `currency_id`, `operation_type`, `is_duty`, plus
  `server_move_id`/`client_move_id` and `server_change_id`/`client_change_id` for the second
  parts of transfers and currency exchanges). Returns the list of `{server_id, client_id,
  status}` maps the server echoes back. `TransactionType` enums are auto-normalised to int.
* `utils.generate_xml_map_array` — companion to `generate_xml_array`, but for arrays whose
  elements are already typed values (typically pre-built `ns2:Map`s from
  `zeep.helpers.create_xml_soap_map`). Required because `generate_xml_array` re-wraps each
  item with `xsd.AnyObject`, which causes pre-built maps to be serialised as Python repr
  strings and the server then refuses them.
* `utils.xmlmap_to_dict` — lightweight `ns2:Map` → `dict[str, str]` parser for write-method
  responses (which return ad-hoc maps, not typed model rows).

## [0.2.0] - 2022-11-12

### Added
* Added timeout options to API class

### Changed
* Some under the hood changes for the repo (src layout, testing)

## [0.1.0] - 2022-08-20

### Added

* Almost full coverage of "get" methods with better English naming for params & types
* Typed data model
