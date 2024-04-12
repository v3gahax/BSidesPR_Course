import argparse
import asyncio
import logging
import json
from pathlib import Path
import httpx

logging.basicConfig()

semaphore = asyncio.Semaphore(50)

async def check_vulnerable(client: httpx.AsyncClient, url: str):
    async with semaphore:
        retries = 3
        while retries > 0:
            try:
                scheme = "http"
                url = f"{scheme}://{url}"
                resp = await client.get(url)
                if resp.status_code == 400:
                    try:
                        scheme = "https"
                        url = f"{scheme}://{url}"
                        resp = await client.get(url)
                    except (httpx.ConnectTimeout, httpx.PoolTimeout, httpx.ReadTimeout, httpx.RemoteProtocolError, httpx.ConnectError):
                        return False

                if resp.status_code == 401:
                    return False

                if resp.status_code == 400:
                    logging.error(f"{url}: 400. Maybe is it an HTTPS host? {resp.text}")
                    return False

                print(f"[+] Found an open orthanc at address {url}")
                resp = await client.get(f"{url}/instances")

                if resp.status_code != 200:
                    logging.error(f"{url}: {resp.status_code} while contacting the API: {resp.text}")
                    return False

                try:
                    res = resp.json()
                except json.decoder.JSONDecodeError:
                    return False
                if not len(res):
                    logging.error(f"{url}: no instances. Not uploading new DICOMs here (yet).")
                    return False

                first = res[0]
                resp = await client.post(f"{url}/instances/{first}/export")

                if resp.status_code == 403:
                    print(f"[-] {url}: PATCHED")
                    return False

                if resp.status_code != 500:
                    logging.warning(f"{url}: {resp}: {resp.text}?")

                print(f"[+] {url}: MAY BE VULNERABLE!")
                return True
            except (httpx.ConnectTimeout, httpx.PoolTimeout, httpx.ReadTimeout, httpx.RemoteProtocolError, httpx.ConnectError, httpx.ReadError):
                retries -= 1
                continue

async def main():
    parser = argparse.ArgumentParser(description='Check for vulnerable hosts.')
    parser.add_argument('hosts_file', help='Path to the hosts file (format: host,port)')
    parser.add_argument('--proxy', help='Proxy settings in the format PROXY_HOST:PROXY_PORT', default=None)
    args = parser.parse_args()

    hostports = [l.strip() for l in Path(args.hosts_file).read_text().splitlines()]
    print(f"Loaded {len(hostports)} hosts.")
    headers = {"Authorization": "Basic b3J0aGFuYzpvcnRoYW5j"}
    
    proxy = args.proxy
    proxies = {"http://": proxy, "https://": proxy} if proxy else None
    
    async with httpx.AsyncClient(follow_redirects=True, headers=headers, verify=False, timeout=15, proxies=proxies) as client:
        tasks = []
        for hostport in hostports:
            host, port = hostport.split(',')
            url = f"{host}:{port}"
            tasks.append(asyncio.ensure_future(check_vulnerable(client, url)))

        scan_result = await asyncio.gather(*tasks)

        print(f"Number of vulnerable hosts: {scan_result.count(True)}")

if __name__ == "__main__":
    asyncio.run(main())
