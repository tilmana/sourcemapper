from datetime import datetime
import time
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
parser.add_argument('-o', '--output', help='Output file (writes valid URLs to specified location for use in reporting or further processing)', required=False)
parser.add_argument('-y', '--force', help='Force processing even for URLs that do not have a ".js" extension', required=False, action='store_true')
parser.add_argument('-e', '--error', help='Override validity check with other positive indicator (this argument\'s text in the response body), for rare instances where .map files are returned even with a 404 status code', required=False)
parser.add_argument('-r', '--redirects', help='Follow redirects', required=False, action='store_true')

args = parser.parse_args()

totalURLs = 0
validURLs = []
validMaps = 0
totalErrors = 0
invalidMaps = 0
now = datetime.now()

print(bcolors.HEADER + "[+] Starting sourcemapper.py ... [+]" + bcolors.ENDC)
print(bcolors.OKBLUE + f"|  Time: {now}  |" + bcolors.ENDC)

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
        if url[-3:] != ".js" and not args.force:
            print(bcolors.FAIL + f"[!] No JS extension, skipping... {url} (use -y to force)" + bcolors.ENDC)
            continue
        if args.url:
            url = args.url + "/" + url.split("/")[-1]
        url = url + ".map"
        totalURLs += 1
        try:
            if args.proxy:
                if args.redirects:
                    r1 = requests.get(url=url, proxies=proxies, verify=False)
                else:
                    r1 = requests.get(url=url, proxies=proxies, verify=False, allow_redirects=False)
            else:
                if args.redirects:
                    r1 = requests.get(url=url, verify=False)
                else:
                    r1 = requests.get(url=url, verify=False, allow_redirects=False)
        except requests.exceptions.ConnectionError:
            print(bcolors.FAIL + f"[!] Connection error when attempting to connect to {url}!" + bcolors.ENDC)
            totalErrors += 1
            continue
        except Exception as e:
            print(bcolors.FAIL + f"[!] Error when attempting to connect to {url}" + bcolors.ENDC)
            totalErrors += 1
            continue
        if r1.status_code == 200:
            validMaps += 1
            validURLs.append(url)
            print(bcolors.OKGREEN + f"[+] Status: {r1.status_code}    Content-Length: {len(r1.text)}    URL: {url}" + bcolors.ENDC)
        elif r1.status_code == 404:
            if args.error:
                if args.error in r1.text:
                    validMaps += 1
                    validURLs.append(url)
                    print(bcolors.OKGREEN + f"[+] Custom Status: {r1.status_code}    Content-Length: {len(r1.text)}    URL: {url}" + bcolors.ENDC)
                else:
                    invalidMaps += 1
                    print(bcolors.FAIL + f"[+] Status: {r1.status_code}    Content-Length: {len(r1.text)}    URL: {url}" + bcolors.ENDC)
            else:
                invalidMaps += 1
                print(bcolors.FAIL + f"[+] Status: {r1.status_code}    Content-Length: {len(r1.text)}    URL: {url}" + bcolors.ENDC)
        elif r1.status_code == 401 or r1.status_code == 403:
            invalidMaps += 1
            print(bcolors.WARNING + f"[+] Status: {r1.status_code}    Content-Length: {len(r1.text)}    URL: {url}" + bcolors.ENDC)
        elif r1.status_code == 301 or r1.status_code == 302:
            invalidMaps += 1
            redirect_url = r1.headers["Location"]
            print(bcolors.WARNING + f"[+] Status: {r1.status_code}  Redirect Location: {redirect_url}    Content-Length: {len(r1.text)}    URL: {url}" + bcolors.ENDC)
        else:
            invalidMaps += 1
            if args.verbose:
                print(bcolors.FAIL + f"[+] Status: {r1.status_code}    Content-Length: {len(r1.text)}    URL: {url}" + bcolors.ENDC)
    print(bcolors.BOLD + "Total Source Maps: " + f"{validMaps}" + bcolors.ENDC)
    if validMaps == 0:
        print(bcolors.BOLD + "Unexpected output? Try with '-v'!")
    if invalidMaps > 0:
        print(bcolors.BOLD + "Total Invalid Files (no source maps returned): " + f"{invalidMaps}" + bcolors.ENDC)
    if totalErrors > 0:
        print(bcolors.BOLD + "Total Errors (invalid or unreachable URLs?): " + f"{totalErrors}" + bcolors.ENDC)
    file1.close()

if args.output:
    fileName = args.output.split(".")
    writeName = ""
    for index in range(len(fileName)):
        if index == len(fileName) - 1:
            writeName += str(now) + "." + fileName[index]
        else:
            writeName += fileName[index] + "."
    writeName = writeName.replace(" ", "_")
    with open(writeName, "w") as file2:
        for index, url in enumerate(validURLs):
            if index == len(validURLs) - 1:
                file2.write(url)
            else:
                file2.write(url + "\n")
    file2.close()
