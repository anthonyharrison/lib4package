# Copyright (C) 2023 Anthony Harrison
# SPDX-License-Identifier: Apache-2.0

import json
import sys

import requests


class Metadata:
    def __init__(self, ecosystem="python", debug=False):
        registry = {
            "cargo":"crates.io",
            "cpan" : "metacpan.org",
            "cran" : "cran.r-project.org",
            "dart": "pub.dev",
            "gem": "rubygems.org",
            "go": "proxy.golang.org",
            "golang": "proxy.golang.org",
            "java": "repo1.maven.org",
            "javascript": "npmjs.org",
            "maven": "repo1.maven.org",
            ".net": "nuget.org",
            "npm": "npmjs.org",
            "nuget": "nuget.org",
            "perl": "metacpan.org",
            "pub": "pub.dev",
            "pypi": "pypi.org",
            "python": "pypi.org",
            "r": "cran.r-project.org",
            "ruby": "rubygems.org",
            "rust": "crates.io",
            "swift": "cocaopod.org",
        }
        self.debug = debug
        self.package_metadata = {}
        self.ecosystem = None
        if ecosystem.lower() in registry:
            self.ecosystem = registry[ecosystem.lower()]
        elif self.debug:
            print (f"Invalid ecosystem {ecosystem} specified.")
        self.package_name = None
        self.package_release_date = None
        self.package_checksum = None
        self.package_version = None

    def get_ecosystem(self):
        return self.ecosystem

    def get_package(self, name, version=None):
        if self.ecosystem is not None:
            url = f"https://packages.ecosyste.ms/api/v1/registries/{self.ecosystem}/packages/{name}"

            if self.debug:
                print(url)
            try:
                self.package_metadata = requests.get(url).json()
                # Check that module has been found
                if self.package_metadata.get("error") is not None:
                    if self.debug:
                        print(f"Unable to find {name} - version {version}")
                    self.package_metadata = {}
                else:
                    self.package_name = name

                # If version specified get additional version specific data
                if version is not None:
                    if self.debug:
                        print (f"Get version specific data for {name}")
                    url = f"{url}/versions/{version}"
                    self.package_metadata_version = requests.get(url).json()
                    if self.package_metadata_version.get("error") is not None:
                        if self.debug:
                            print(f"Unable to get version specific data for {name}")
                        self.package_metadata = {}
                    else:
                        # And extract checksum and published date
                        self.package_release_date = self.package_metadata_version.get("published_at")
                        self.package_checksum = self.package_metadata_version.get("integrity")
                        self.package_version = version
            except:
                # Potential JSON error
                self.package_metadata = {}

    def _check(self):
        return len(self.package_metadata) > 0

    def _check_data(self):
        return self.package_metadata.get("repo_metadata") is not None

    def get_data(self):
        return self.package_metadata

    def print_data(self):
        json.dump(self.package_metadata, sys.stdout, indent="    ")

    # Get attributes
    def show_checksum(self, version=None):
        if self._check() and self._check_data():
            if self.package_checksum is not None:
                print (f"{self.package_version} - {self.package_checksum}")
            elif "tags" in self.package_metadata["repo_metadata"]:
                for tag in self.package_metadata["repo_metadata"]["tags"]:
                    if version is not None:
                        if version in tag["name"]:
                            print(f"{tag['name']} - {tag['sha']}")
                    else:
                        print(f"{tag['name']} - {tag['sha']}")

    def get_checksum(self, version=None):
        if self._check() and self._check_data():
            if self.package_checksum is not None:
                return self.package_checksum.replace("sha256-",""), "SHA256"
            if "tags" in self.package_metadata["repo_metadata"]:
                if version is not None:
                    for tag in self.package_metadata["repo_metadata"]["tags"]:
                        if version in tag["name"]:
                            return tag["sha"], "SHA1"
                else:
                    # Return latest
                    latest_version = self.get_latest_version()
                    # Check that there are tags!
                    if len(self.package_metadata["repo_metadata"]["tags"]) > 0:
                        # Check latest version matches the tag
                        if (
                            latest_version
                            in self.package_metadata["repo_metadata"]["tags"][0]["name"]
                        ):
                            return self.package_metadata["repo_metadata"]["tags"][0]["sha"], "SHA1"
        return None, None

    def get_value(self, key, default=None):
        if not self._check():
            return None
        value = self.package_metadata.get(key, default)
        if value is not None:
            # Remove any newlines or double spaces in any string
            return str(value).replace("\n", " ").replace("  ", " ").strip()
        return value

    def get_description(self):
        return self.get_value("description")

    def get_homepage(self):
        return self.get_value("homepage")

    def get_license(self):
        the_licence = ""
        if self._check() and self._check_data():
            if self.debug:
                print(f"Extract licenses for {self.package_name}")
            if "licenses" in self.package_metadata["repo_metadata"]:
                the_licence = self.package_metadata["repo_metadata"]["license"]
            else:
                the_licence = self.get_value("licenses", "")
            if the_licence is not None:
                # Might be multiple licenses
                license_list = the_licence.split(",")
                the_licence = ""
                for license in license_list:
                    the_licence = f"{the_licence} {license.strip()} AND"
                # Remove extraneous " AND "
                the_licence = the_licence[:-4].strip()

        return the_licence

    def get_no_of_versions(self):
        return int(self.get_value("versions_count"))

    def get_no_of_updates(self, version):
        # Get number of updated versions
        updated_versions = 0
        if self._check() and self._check_data():
            if "tags" in self.package_metadata["repo_metadata"]:
                for tag in self.package_metadata["repo_metadata"]["tags"]:
                    if version == tag["name"].lower().replace("v",""):
                        return updated_versions
                    else:
                        updated_versions += 1
        return updated_versions

    def get_latest_release(self):
        return self.get_value("latest_release_number")

    def get_latest_version(self):
        return self.get_latest_release()

    def get_latest_release_time(self):
        if self.package_release_date is not None:
            return self.package_release_date
        return self.get_value("latest_release_published_at")

    def get_downloadlocation(self):
        return self.get_value("registry_url")

    def get_originator(self):
        if self._check() and self._check_data():
            try:
                owner = self.package_metadata["repo_metadata"]["owner_record"]["name"]
                email = self.package_metadata["repo_metadata"]["owner_record"]["email"]
                if owner is None:
                    owner = self.package_metadata["repo_metadata"]["owner"]
                if email is not None and len(email) > 0:
                    return f"{owner} ({email})"
                else:
                    return f"{owner} "
            except KeyError:
                return None
        else:
            return None

    def get_purl(self):
        if self._check():
            return self.package_metadata["purl"]
        return None
