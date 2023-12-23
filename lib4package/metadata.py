# Copyright (C) 2023 Anthony Harrison
# SPDX-License-Identifier: Apache-2.0

import json
import sys

import requests


class Metadata:
    def __init__(self, ecosystem="python", debug=False):
        registry = {
            "dart": "pub.dev",
            "go": "proxy.golang.org",
            "java": "repo1.maven.org",
            "javascript": "npmjs.org",
            ".net": "nuget.org",
            "perl": "metacpan.org",
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
        self.package_name = None

    def get_ecosystem(self):
        return self.ecosystem

    def get_package(self, name, version=None):
        if self.ecosystem is not None:
            url = f"https://packages.ecosyste.ms/api/v1/registries/{self.ecosystem}/packages/{name}"
            if version is not None:
                url = f"{url}/versions/{version}"

            if self.debug:
                print(url)
            self.package_metadata = requests.get(url).json()
            # Check that module has been found
            if self.package_metadata.get("error") is not None:
                if self.debug:
                    print(f"Unable to find {name} - version {version}")
                self.package_metadata = {}
            else:
                self.package_name = name

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
            if "tags" in self.package_metadata["repo_metadata"]:
                for tag in self.package_metadata["repo_metadata"]["tags"]:
                    if version is not None:
                        if version in tag["name"]:
                            print(f"{tag['name']} - {tag['sha']}")
                    else:
                        print(f"{tag['name']} - {tag['sha']}")

    def get_checksum(self, version=None):
        if self._check() and self._check_data():
            if "tags" in self.package_metadata["repo_metadata"]:
                if version is not None:
                    for tag in self.package_metadata["repo_metadata"]["tags"]:
                        if version in tag["name"]:
                            return tag["sha"]
                else:
                    # Return latest
                    latest_version = self.get_latest_version()
                    # Check latest version matches the tag
                    if (
                        latest_version
                        in self.package_metadata["repo_metadata"]["tags"][0]["name"]
                    ):
                        return self.package_metadata["repo_metadata"]["tags"][0]["sha"]
        return None

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
        the_licence = None
        if self._check() and self._check_data():
            if self.debug:
                print(f"Extract licenses for {self.package_name}")
            if "licenses" in self.package_metadata["repo_metadata"]:
                the_licence = self.package_metadata["repo_metadata"]["license"]
            else:
                the_licence = self.get_value("licenses", "")
        return the_licence

    def get_no_of_versions(self):
        return int(self.get_value("versions_count"))

    def get_no_of_updates(self, version):
        # Get number of updated versions
        updated_versions = 0
        if self._check() and self._check_data():
            if "tags" in self.package_metadata["repo_metadata"]:
                for tag in self.package_metadata["repo_metadata"]["tags"]:
                    if version in tag["name"]:
                        return updated_versions
                    else:
                        updated_versions += 1
        return updated_versions

    def get_latest_release(self):
        return self.get_value("latest_release_number")

    def get_latest_version(self):
        return self.get_latest_release()

    def get_latest_release_time(self):
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
