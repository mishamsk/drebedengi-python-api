# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
* `api.delete_object(object_id=..., object_type=...)` — wraps the `deleteObject` SOAP method.
  `object_type` is a `Literal[...]` of the eight WSDL-allowed kinds (``waste``, ``income``,
  ``move``, ``change``, ``object``, ``currency``, ``tag``, ``accum``). Returns `True` on
  success, raises `DrebedengiAPIError` on the "other object connected" failure mode so the
  caller can clean dependants up.
* `DeletableObjectType` — exported `Literal` alias for the eight valid `object_type` values.

## [0.2.0] - 2022-11-12

### Added
* Added timeout options to API class

### Changed
* Some under the hood changes for the repo (src layout, testing)

## [0.1.0] - 2022-08-20

### Added

* Almost full coverage of "get" methods with better English naming for params & types
* Typed data model
