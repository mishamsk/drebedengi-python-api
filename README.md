# Drebedengi Python API

[![pypi](https://img.shields.io/pypi/v/drebedengi-python-api.svg)](https://pypi.org/project/drebedengi-python-api/)
[![python](https://img.shields.io/pypi/pyversions/drebedengi-python-api.svg)](https://pypi.org/project/drebedengi-python-api/)
[![Build Status](https://github.com/mishamsk/drebedengi-python-api/actions/workflows/dev.yml/badge.svg)](https://github.com/mishamsk/drebedengi-python-api/actions/workflows/dev.yml)


A rather thin python wrapper for Drebedengi SOAP API.


* Documentation: <https://mishamsk.github.io/drebedengi-python-api>
* GitHub: <https://github.com/mishamsk/drebedengi-python-api>
* PyPI: <https://pypi.org/project/drebedengi-python-api/>
* Free software: GPL-3.0-only


## Features

* Almost full coverage of "get" methods with better English naming for params & types (see [drebedengi.api][])
!!! important
    Retrieving aggregated reports via `get_transactions` is not currently supported, despite full list of API parameters
* Typed data model (see [drebedengi.model][])

## Credits

Thanks to:

- [drebedengi](https://www.drebedengi.ru/) for a great finance management service
- [zeep](https://docs.python-zeep.org/en/master/index.html) for a convenient Python SOAP client
- [lxml](https://lxml.de) for XML library
- [attrs](https://www.attrs.org/en/stable/index.html) for model classes

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [mishamsk/cookiecutter-pypackage](https://github.com/mishamsk/cookiecutter-pypackage) project template.
