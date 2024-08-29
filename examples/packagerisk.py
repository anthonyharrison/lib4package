from lib4package.metadata import Metadata
import sys

m = Metadata("python", debug=False)
m.get_package(sys.argv[1])
packdata = m.get_data()
versions = {}
for i in packdata['repo_metadata']['tags']:
    x = i['name'].lower()
    if x.startswith('version-'):
        x = x[8:]
    elif x.startswith('v'):
        x=x[1:]
    versions[x] = False
    print (x)
for a in packdata['advisories']:
    for p in a['packages']:
        for v in p['versions']:
            version = v['vulnerable_version_range']
            # Parse version
            for i in version.split(','):
                print (i)
                version_type = i[0]
                if version_type == "<":
                    end_version = i[1:].strip()
                    start_version = False
                    for s in versions:
                        if start_version:
                            versions[s] = True
                        elif s == end_version:
                            start_version = True
                elif version_type == "<=":
                    end_version = i[1:].strip()
                    start_version = False
                    for s in versions:
                        if start_version:
                            versions[s] = True
                        elif s == end_version:
                            start_version = True
                            versions[s] = True
                elif version_type == "=":
                    versions[i[1:].strip()] = True

vuln_versions = 0
for v in versions:
    if versions[v]:
        vuln_versions += 1

print ("Number of versions", len(versions))
print ("Number of vulnerable versions", vuln_versions)
print ("Vuln Potential Score", vuln_versions/len(versions))

