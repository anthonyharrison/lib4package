# Lib4package

Lib4package is a library to handle package metadata to be included in a Software Bill of Materials (SBOMs). The data should be suitable for SBOMs created in both
[SPDX](https://www.spdx.org) and [CycloneDX](https://www.cyclonedx.org) formats.

It has been developed on the assumption that having a common way of obtaining component metadata regardless of the language ecosystem will be useful to developers.

## Installation

To install use the following command:

`pip install lib4package`

Alternatively, just clone the repo and install dependencies using the following command:

`pip install -U -r requirements.txt`

The tool requires Python 3 (3.8+). It is recommended to use a virtual python environment especially
if you are using different versions of python. `virtualenv` is a tool for setting up virtual python environments which
allows you to have all the dependencies for the tool set up in a single environment, or have different environments set
up for testing using different versions of Python.

## API

### Metadata

The Metadata module provides methods for accessing the component data from a language ecosystem.
The focus of the implementation is on providing a common set of methods regardless of the language ecosystem.

_class_ **Metadata**(_ecosystem="python"_, _debug=False_)

This creates a simple Metadata object. The object takes two optional parameters, _ecosystem_,
which represents the language ecosystem to use (the default is Python), and _debug_ which is used to enable
the generation of debugging information (the default is False). The appropriate [PURL](https://github.com/package-url/purl-spec)
type can also be specified for the ecosystem e.g. pypi for Python.

The following language ecosystems are supported:

- dart
- go
- java
- javascript
- .net
- perl
- php
- python
- r
- ruby
- rust
- swift

Invalid ecosystems will have no affect.

**Methods**

_**get_package(name,_version=None_)**_
Retrieves the data for the specified package. If the version is not specified (the default), the data for the latest version is
retrieved.

**_get_data()_**
Returns a JSON object containing all the metadata for the package.

**_print_data()_**
Prints the metadata for the package.

**_get_checksum(_version=None_)_**
Return the SHA1 checksum for the specified version of the package. If the version is not specified, the checksum for the latest version is returned. **NOTE** that a checksum might not be available for the latest version, in which case None will be returned.

**_get_description()_**
Return the package description. None is returned if no description found.

**_get_license()_**
Return the license for the package. If no license is found, None is returned.

**_get_homepage()_**
Return the URL of the homepage for the package. None is returned if no homepage is available.

**_get_downloadlocation()_**
Return the URL of the download location for the package. None is returned if no download location is available.

**_get_purl()_**
Return the Package URL (PURL) of the package. None is returned if it is not available.

**_get_originator()_**
Return the originator of the package and optionally, an email address. If no originator can be found, None is returned.

**_get_latest_release()_**
Returns the name of the latest release of the package. If no package data is available, None is returned.

**_get_latest_release_time()_**
Returns the time when the latest release of the package was released. If no package data is available, None is returned.

**_get_no_of_versions()_**
Returns the number of releases of the package.

**_get_no_of_updates(version)_**
Returns the number of updates from the specified version to the latest version.

**Example**

The following code sample shows the use of the Metadata module.

```python
>>> from lib4package.metadata import Metadata
>>> meta = Metadata(ecosystem="Python")
>>> meta.get_package("requests")
>>> meta.get_latest_release()
'0.12.01'
>>> meta.get_description()
'Python HTTP for Humans.'
>>> meta.get_originator()
'Python Software Foundation '
>>> meta.get_license()
'Apache 2.0'                                                                                                                                                             
>>> meta = Metadata(ecosystem="java")
>>> meta.get_package("org.slf4j:slf4j-api")
>>> meta.get_latest_version()
'2.0.9'
>>> meta.get_description()
'The slf4j API'
>>> meta.get_checksum()
>>> meta.get_license()
'MIT License'
>>> meta.get_no_of_versions()
96
>>> m.get_checksum("2.0.6")
'5ff6f2c385c36ea4f8b85cacd69f7ca891c37818'
```

## License

Licensed under the Apache 2.0 Licence.

## Limitations

This tool is meant to support software development. The usefulness of the tool is dependent on the metadata
which is provided to the tool from the language ecosystems. Unfortunately, the tool is unable to determine the validity or
completeness of sthe data; users of the tool are therefore reminded that they should assert the quality of any data which is provided to the tool.

## Feedback and Contributions

Bugs and feature requests can be made via GitHub Issues.