from datetime import datetime
import requests
import argparse

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

parser = argparse.ArgumentParser(description="""Script to help in locating JavaScript source maps given a large list of URLs """)
parser.add_argument('-f', '--file', help='File containing list of JavaScript URLs', required=True)
parser.add_argument('-d', '--delimiter', help='Specify alternative delimiter (default new line)', required=False, default="\n")
parser.add_argument('-u', '--url', help='Specify alternative URL and port (test production for example)', required=False)
parser.add_argument('-p', '--proxy', help='Specify proxy (such as Burp Suite)', required=False)
parser.add_argument('-v', '--verbose', help='Enable verbosity (returns responses for all URLs instead of only successful/blocked)', required=False, action='store_true')

args = parser.parse_args()

totalURLs = 0
totalMaps = 0
now = datetime.now()

print(bcolors.HEADER + "[+] Starting sourcemapper.py ... [+]" + bcolors.ENDC)
print(bcolors.OKBLUE + f"|  Time: {now}  |" + bcolors.ENDC + "\n")

if args.proxy:
    proxies = {
        "http": args.proxy,
        "https": args.proxy
    }

with open(args.file, "r") as file1:
    file1content = file1.read().split(args.delimiter)
    if file1content[-1] == "":
        file1content = file1content[:-1]
    for url in file1content:
        if args.url:
            url = args.url + "/" + url.split("/")[-1]
        url = url + ".map"
        totalURLs += 1
        if args.proxy:
            r1 = requests.get(url=url, proxies=proxies, verify=False)
        else:
            r1 = requests.get(url=url, verify=False)
        if args.verbose:
            if r1.status_code == 200:
                totalMaps += 1
                print(bcolors.OKGREEN + f"[+]           Status: {r1.status_code}    Content-Length: {len(r1.text)}    URL: {url}" + bcolors.ENDC)
            elif str(r1.status_code)[0] == "4":
                print(bcolors.FAIL + f"[+]           Status: {r1.status_code}    Content-Length: {len(r1.text)}    URL: {url}" + bcolors.ENDC)
        else:
            if r1.status_code == 200:
                totalMaps += 1
                print(bcolors.OKGREEN + f"[+]           Status: {r1.status_code}    Content-Length: {len(r1.text)}    URL: {url}" + bcolors.ENDC)
            elif str(r1.status_code)[0] == "4" and r1.status_code != 404:
                print(bcolors.FAIL + f"[+]           Status: {r1.status_code}    Content-Length: {len(r1.text)}    URL: {url}" + bcolors.ENDC)
    print("\n")
    print(bcolors.BOLD + "Total Source Maps: " + f"{totalMaps}" + bcolors.ENDC)
    file1.close()
