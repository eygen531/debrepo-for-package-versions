import requests
import os
import re
import glob
import argparse
import shutil
import sys


def download_packages(server, os_name, arch, packages_file):
    found_package = True
    target_dir = os.path.join(os.getcwd(), os_name)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    with open(packages_file) as file:
        package_order = []
        for line in file.readlines():
            split_list = line.rstrip('\n').split('=')

            if len(split_list) == 0:
                continue

            url_params = 'pckg=' + split_list[0]

            if len(split_list) == 2:
                url_params = url_params + '&ver=' + split_list[1]

            download_url = server + os_name + '/?' + url_params + '&arch=' + arch

            print(split_list[0])
            print(download_url)

            r = requests.get(download_url, allow_redirects=True)
            content_disposition = r.headers.get("content-disposition")
            if content_disposition:
                filename = re.findall("filename=(\S+)", content_disposition)[0].replace('"', '')
            else:
                found_package = False

            package_order.append(filename)

            if not found_package:
                print("Error: No package found. {}".format(download_url))
                if args.remove:
                    delete_packages(target_dir)
                sys.exit(1)

            with open(os.path.join(target_dir, filename), 'wb') as f:
                f.write(r.content)

    return package_order


def install_packages(packages, target_dir):
    for package in packages:
        result = os.system("dpkg -i {}".format(os.path.join(target_dir, package)))
        if result != 0:
            print("Error installing package: {}".format(package))
            if args.remove:
                delete_packages(target_dir)
            sys.exit(1)


def delete_packages(target_dir):
    for file in glob.glob(os.path.join(target_dir, "*.deb")):
        os.remove(file)
        print("Deleted {}".format(file))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and optionally install or delete .deb packages")
    parser.add_argument("--server", "-s", help="Repository server URL")
    parser.add_argument("--os_name", "-o", help="Operating system name")
    parser.add_argument("--arch", "-a", help="Architecture")
    parser.add_argument("--packages_file", "-p", help="File containing package names")
    parser.add_argument("-i", "--install", action="store_true", help="Install downloaded packages")
    parser.add_argument("-r", "--remove", action="store_true", help="Remove downloaded packages")

    args = parser.parse_args()

    package_order = download_packages(args.server, args.os_name, args.arch, args.packages_file)

    if args.install:
        install_packages(package_order, args.os_name)

    if args.remove:
        delete_packages(args.os_name)
