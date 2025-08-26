import requests
import re
from packaging import version
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

proxies = None  # 不使用代理

# 定义当前版本和应用环境
current_versions = {
    "binutils": "2.45",
    "c-ares": "1.34.5",
    "expat": "2.7.1",
    "gcc": "15.2.0",
    "gettext-tools-windows": "0.25",
    "gmp": "6.3.0",
    "gnutls": "3.8.10",
    "gpg-error": "1.55",
    "gpgme": "2.0.0",
    "isl": "0.27",
    "libassuan": "3.0.2",
    "libiconv": "1.18",
    "libidn2": "2.3.8",
    "libmetalink": "0.1.3",
    "libmicrohttpd": "1.0.2",
    "libpsl": "0.21.5",
    "libssh2": "1.11.1",
    "libtasn1": "4.20.0",
    "libunistring": "1.3",
    "libxml2": "2.14.5",
    "mpc": "1.3.1",
    "mpfr": "4.2.2",
    "nettle": "3.10.2",
    "nghttp2": "1.66.0",
    "openssl": "3.5.2",
    "pcre2": "10.45",
    "sqlite": "3.50.4",
    "xz": "5.8.1",
    "zlib": "1.3.1",
    "zlib-ng": "2.2.5",
    "zstd": "1.5.7",
}

# 定义程序应用环境的备注
program_environments = {
    "binutils": "musl-cross、mingw_w64",
    "c-ares": "wget、aria2c0、aria2c、aria2c1",
    "expat": "wget、aria2c",
    "gcc": "musl-cross、mingw_w64",
    "gettext-tools-windows": "aria2c0",
    "gmp": "wget、wget2、aria2c、musl-cross",
    "gnutls": "wget、wget2",
    "gpg-error": "wget",
    "gpgme": "wget",
    "isl": "musl-cross",
    "libassuan": "wget",
    "libiconv": "wget、wget2",
    "libidn2": "wget、wget2",
    "libmetalink": "wget",
    "libmicrohttpd": "wget2",
    "libpsl": "wget、wget2",
    "libssh2": "aria2c0、aria2c、aria2c1",
    "libtasn1": "wget、wget2",
    "libunistring": "wget、wget2",
    "libxml2": "aria2c1",
    "mpc": "musl-cross",
    "mpfr": "musl-cross",
    "nettle": "wget、wget2",
    "nghttp2": "wget2",
    "openssl":"wget",
    "pcre2": "wget、wget2",
    "sqlite": "aria2c0、aria2c、aria2c1",
    "xz": "wget2、aria2c1",
    "zlib": "aria2c、aria2c0、musl-cross",
    "zlib-ng": "aria2c1",
    "zstd": "wget2、musl-cross",
}

def retry(func, url, max_retries=5, delay=2, proxies=None, program=None):
    attempts = 0
    while attempts < max_retries:
        try:
            response = func(url, proxies=proxies)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            attempts += 1
            if attempts == max_retries:
                raise e
            time.sleep(delay)

def get_latest_version(program, proxies=None):
    if program == "zlib":
        url = "https://api.github.com/repos/madler/zlib/releases/latest"
        response = retry(requests.get, url, proxies=proxies,program=program)
        data = response.json()
        latest_version = data["tag_name"].lstrip("v")
        download_url = data["assets"][0]["browser_download_url"]
        return latest_version, download_url

    elif program == "zstd":
        url = "https://api.github.com/repos/facebook/zstd/releases/latest"
        response = retry(requests.get, url, proxies=proxies,program=program)
        data = response.json()
        latest_version = data["tag_name"].lstrip("v")
        download_url = data["assets"][0]["browser_download_url"]
        return latest_version, download_url

    elif program == "gmp":
        url = "https://ftp.gnu.org/gnu/gmp/"
        response = retry(requests.get, url, proxies=proxies,program=program)
        matches = re.findall(r'href="gmp-([0-9.]+)\.tar\.(xz|gz)"', response.text)
        latest_version = max(matches, key=lambda x: version.parse(x[0]))[0]
        download_url = f"https://ftp.gnu.org/gnu/gmp/gmp-{latest_version}.tar.xz"
        return latest_version, download_url

    elif program == "isl":
        url = "https://libisl.sourceforge.io/"
        response = retry(requests.get, url, proxies=proxies,program=program)
        matches = re.findall(r'href="isl-([\d.]+)\.tar\.xz"', response.text)
        if not matches:
            return current_versions["isl"], f"https://libisl.sourceforge.io/isl-{current_versions['isl']}.tar.xz"
        latest_version = max(matches, key=version.parse)
        download_url = f"https://libisl.sourceforge.io/isl-{latest_version}.tar.xz"
        return latest_version, download_url

    elif program == "mpfr":
        url = "https://ftp.gnu.org/gnu/mpfr/"
        response = retry(requests.get, url, proxies=proxies,program=program)
        matches = re.findall(r'href="mpfr-([0-9.]+)\.tar\.(xz|gz)"', response.text)
        latest_version = max(matches, key=lambda x: version.parse(x[0]))[0]
        download_url = f"https://ftp.gnu.org/gnu/mpfr/mpfr-{latest_version}.tar.xz"
        return latest_version, download_url

    elif program == "mpc":
        url = "https://ftp.gnu.org/gnu/mpc/"
        response = retry(requests.get, url, proxies=proxies,program=program)
        matches = re.findall(r'href="mpc-([0-9.]+)\.tar\.(gz|xz)"', response.text)
        latest_version = max(matches, key=lambda x: version.parse(x[0]))[0]
        download_url = f"https://ftp.gnu.org/gnu/mpc/mpc-{latest_version}.tar.gz"
        return latest_version, download_url

    elif program == "binutils":
        url = "https://ftp.gnu.org/gnu/binutils/"
        response = retry(requests.get, url, proxies=proxies,program=program)
        matches = re.findall(r'href="binutils-([0-9.]+)\.tar\.(xz|gz)"', response.text)
        latest_version = max(matches, key=lambda x: version.parse(x[0]))[0]
        download_url = f"https://ftp.gnu.org/gnu/binutils/binutils-{latest_version}.tar.xz"
        return latest_version, download_url

    elif program == "gcc":
        url = "https://ftp.gnu.org/gnu/gcc/"
        response = retry(requests.get, url, proxies=proxies,program=program)
        matches = re.findall(r'href="gcc-([0-9.]+)/"', response.text)
        if not matches:
            return current_versions["gcc"], f"https://ftp.gnu.org/gnu/gcc/gcc-{current_versions['gcc']}/gcc-{current_versions['gcc']}.tar.xz"

        version_matches = [m for m in matches if re.match(r"^\d+(\.\d+)+$", m)]
        if not version_matches:
            return current_versions["gcc"], f"https://ftp.gnu.org/gnu/gcc/gcc-{current_versions['gcc']}/gcc-{current_versions['gcc']}.tar.xz"

        latest_version = max(version_matches, key=version.parse)
        download_url = f"https://ftp.gnu.org/gnu/gcc/gcc-{latest_version}/gcc-{latest_version}.tar.xz"
        return latest_version, download_url

    elif program == "nettle":
        url = "https://ftp.gnu.org/gnu/nettle/"
        response = retry(requests.get, url, proxies=proxies,program=program)
        matches = re.findall(r'href="nettle-([0-9.]+)\.tar\.(gz|xz)"', response.text)
        latest_version = max(matches, key=lambda x: version.parse(x[0]))[0]
        download_url = f"https://ftp.gnu.org/gnu/nettle/nettle-{latest_version}.tar.gz" # Correct URL - using latest_version
        return latest_version, download_url


    elif program == "libtasn1":
        url = "https://ftp.gnu.org/gnu/libtasn1/"
        response = retry(requests.get, url, proxies=proxies,program=program)
        matches = re.findall(r'href="libtasn1-([0-9.]+)\.tar\.(gz|xz)"', response.text)
        latest_version = max(matches, key=lambda x: version.parse(x[0]))[0]
        download_url = f"https://ftp.gnu.org/gnu/libtasn1/libtasn1-{latest_version}.tar.gz" # Correct URL - using latest_version
        return latest_version, download_url

    elif program == "libunistring":
        url = "https://ftp.gnu.org/gnu/libunistring/"
        response = retry(requests.get, url, proxies=proxies,program=program)
        matches = re.findall(r'href="libunistring-([0-9.]+)\.tar\.(gz|xz)"', response.text)
        latest_version = max(matches, key=lambda x: version.parse(x[0]))[0]
        download_url = f"https://ftp.gnu.org/gnu/libunistring/libunistring-{latest_version}.tar.gz" # Correct URL - using latest_version
        return latest_version, download_url

    elif program == "gpg-error":
        url = "https://www.gnupg.org/ftp/gcrypt/libgpg-error/"
        response = retry(requests.get, url, proxies=proxies,program=program)
        matches = re.findall(r'href="libgpg-error-([0-9.]+)\.tar\.(gz|xz)"', response.text)
        latest_version = max(matches, key=lambda x: version.parse(x[0]))[0]
        download_url = f"https://www.gnupg.org/ftp/gcrypt/libgpg-error/libgpg-error-{latest_version}.tar.gz" # Correct URL - using latest_version
        return latest_version, download_url

    elif program == "libassuan":
        url = "https://www.gnupg.org/ftp/gcrypt/libassuan/"
        response = retry(requests.get, url, proxies=proxies,program=program)
        matches = re.findall(r'href="libassuan-([0-9.]+)\.tar\.(bz2|xz)"', response.text)
        latest_version = max(matches, key=lambda x: version.parse(x[0]))[0]
        download_url = f"https://www.gnupg.org/ftp/gcrypt/libassuan/libassuan-{latest_version}.tar.bz2" # Correct URL - using latest_version
        return latest_version, download_url

    elif program == "gpgme":
        url = "https://www.gnupg.org/ftp/gcrypt/gpgme/"
        response = retry(requests.get, url, proxies=proxies,program=program)
        matches = re.findall(r'href="gpgme-([0-9.]+)\.tar\.(bz2|xz)"', response.text)
        latest_version = max(matches, key=lambda x: version.parse(x[0]))[0]
        download_url = f"https://www.gnupg.org/ftp/gcrypt/gpgme/gpgme-{latest_version}.tar.bz2" # Correct URL - using latest_version
        return latest_version, download_url

    elif program == "c-ares":
        url = "https://api.github.com/repos/c-ares/c-ares/releases/latest"
        response = retry(requests.get, url, proxies=proxies,program=program)
        data = response.json()
        latest_version = data["tag_name"].lstrip("v")
        for asset in data["assets"]:
            if asset["name"].endswith(".tar.gz"):
                download_url = asset["browser_download_url"]
                return latest_version, download_url
        download_url = data["assets"][0]["browser_download_url"]
        return latest_version, download_url
        
    elif program == "gettext-tools-windows":
        url = "https://api.github.com/repos/vslavik/gettext-tools-windows/releases/latest"
        response = retry(requests.get, url, proxies=proxies,program=program)
        data = response.json()
        latest_version = data["tag_name"].lstrip("v")
        for asset in data["assets"]:
            if asset["name"].endswith(".zip"):
                download_url = asset["browser_download_url"]
                return latest_version, download_url
        download_url = data["assets"][0]["browser_download_url"]
        return latest_version, download_url

    elif program == "libiconv":
        url = "https://ftp.gnu.org/gnu/libiconv/"
        response = retry(requests.get, url, proxies=proxies,program=program)
        matches = re.findall(r'href="libiconv-([0-9.]+)\.tar\.(gz|xz)"', response.text)
        latest_version = max(matches, key=lambda x: version.parse(x[0]))[0]
        download_url = f"https://ftp.gnu.org/gnu/libiconv/libiconv-{latest_version}.tar.gz" # Correct URL - using latest_version
        return latest_version, download_url

    elif program == "libidn2":
        url = "https://ftp.gnu.org/gnu/libidn/"
        response = retry(requests.get, url, proxies=proxies,program=program)
        matches = re.findall(r'href="libidn2-([0-9.]+)\.tar\.(gz|xz)"', response.text)
        latest_version = max(matches, key=lambda x: version.parse(x[0]))[0]
        download_url = f"https://ftp.gnu.org/gnu/libidn/libidn2-{latest_version}.tar.gz" # Correct URL - using latest_version
        return latest_version, download_url

    elif program == "libpsl":
        url = "https://api.github.com/repos/rockdaboot/libpsl/releases/latest"
        response = retry(requests.get, url, proxies=proxies,program=program)
        data = response.json()
        latest_version = data["tag_name"].lstrip("v")
        download_url = data["assets"][0]["browser_download_url"]
        return latest_version, download_url

    elif program == "pcre2":
        url = "https://api.github.com/repos/PCRE2Project/pcre2/releases/latest"
        response = retry(requests.get, url, proxies=proxies,program=program)
        data = response.json()
        latest_version = data["tag_name"].replace('pcre2-', '')
        download_url = data["assets"][0]["browser_download_url"]
        return latest_version, download_url

    elif program == "expat":
        url = "https://api.github.com/repos/libexpat/libexpat/releases/latest"
        response = retry(requests.get, url, proxies=proxies,program=program)
        data = response.json()
        latest_version = data["tag_name"].lstrip("R_").replace('_', '.')
        download_url = data["assets"][0]["browser_download_url"]
        return latest_version, download_url
        
    elif program == "openssl":
        url = "https://api.github.com/repos/openssl/openssl/releases/latest"
        response = retry(requests.get, url, proxies=proxies, program=program)
        data = response.json()
        tag_name = data["tag_name"]
        latest_version = tag_name.lstrip("openssl-")
        download_url = None
        for asset in data["assets"]:
            if asset["name"].endswith(".tar.gz"):
                download_url = asset["browser_download_url"]
                break 
        if not download_url:
            raise ValueError("Could not find the .tar.gz source archive in OpenSSL release assets.")
        return latest_version, download_url

    elif program == "libmetalink":
        url = "https://api.github.com/repos/metalink-dev/libmetalink/releases/latest"
        response = retry(requests.get, url, proxies=proxies,program=program)
        data = response.json()
        latest_version = data["tag_name"].lstrip("release-")
        download_url = data["assets"][0]["browser_download_url"]
        return latest_version, download_url

    elif program == "gnutls":
        base_url = "https://www.gnupg.org/ftp/gcrypt/gnutls/"
        response = retry(requests.get, base_url, proxies=proxies,program=program)
        version_dir_matches = re.findall(r'href="v([\d.]+)"', response.text)
        if not version_dir_matches:
            return current_versions["gnutls"], f"https://www.gnupg.org/ftp/gcrypt/gnutls/gnutls-{current_versions['gnutls']}.tar.xz"
        latest_version_dir = max(version_dir_matches, key=version.parse)
        version_url = base_url + f"v{latest_version_dir}/"
        version_response = retry(requests.get, version_url, proxies=proxies,program=program)
        matches = re.findall(r'href="gnutls-([\d.]+)\.tar\.xz"', version_response.text)
        if not matches:
             return current_versions["gnutls"], f"https://www.gnupg.org/ftp/gcrypt/gnutls/gnutls-{current_versions['gnutls']}.tar.xz"
        latest_version = max(matches, key=version.parse) # Corrected max call with version.parse as key
        download_url = f"https://www.gnupg.org/ftp/gcrypt/gnutls/v{latest_version_dir}/gnutls-{latest_version}.tar.xz"
        return latest_version, download_url

    elif program == "nghttp2":
        url = "https://api.github.com/repos/nghttp2/nghttp2/releases/latest"
        response = retry(requests.get, url, proxies=proxies,program=program)
        data = response.json()
        latest_version = data["tag_name"].lstrip("v")
        for asset in data["assets"]:
            if asset["name"].endswith(".tar.gz"):
                download_url = asset["browser_download_url"]
                return latest_version, download_url
        download_url = data["assets"][0]["browser_download_url"] # Fallback
        return latest_version, download_url


    elif program == "libmicrohttpd":
        url = "https://ftp.gnu.org/gnu/libmicrohttpd/"
        response = retry(requests.get, url, proxies=proxies,program=program)
        matches = re.findall(r'href="libmicrohttpd-([0-9.]+)\.tar\.(gz|xz)"', response.text)
        latest_version = max(matches, key=lambda x: version.parse(x[0]))[0]
        download_url = f"https://ftp.gnu.org/gnu/libmicrohttpd/libmicrohttpd-{latest_version}.tar.gz"
        return latest_version, download_url

    elif program == "zlib-ng":
        url = "https://api.github.com/repos/zlib-ng/zlib-ng/releases/latest"
        response = retry(requests.get, url, proxies=proxies, program=program)
        data = response.json()
        latest_version = data["tag_name"].lstrip("v")
        download_url = data["assets"][0]["browser_download_url"]
        return latest_version, download_url

    elif program == "libssh2":
        url = "https://libssh2.org/download/"
        response = retry(requests.get, url, proxies=proxies, program=program)
        matches = re.findall(r'href="libssh2-([0-9.]+)\.tar\.(xz|gz)"', response.text)
        latest_version = max(matches, key=lambda x: version.parse(x[0]))[0]
        download_url = f"https://libssh2.org/download/libssh2-{latest_version}.tar.xz"
        return latest_version, download_url

    elif program == "libxml2":
        base_url = "https://download.gnome.org/sources/libxml2/"
        response = retry(requests.get, base_url, program=program, proxies=proxies)
        html = response.text
        main_versions = re.findall(r'href="(\d+\.\d+/)"', html)
        main_versions = [v.strip('/') for v in main_versions]
        main_versions.sort(key=lambda v: version.parse(v), reverse=True)
        latest_main = main_versions[0]
        response = retry(requests.get, f"{base_url}{latest_main}/", program=program, proxies=proxies)
        html = response.text
        files = re.findall(r'href="(libxml2-(\d+\.\d+\.\d+)\.tar\.xz)"', html)
        latest_file = max(files, key=lambda x: version.parse(x[1]))
        download_url = f"{base_url}{latest_main}/{latest_file[0]}"
        latest_version = latest_file[1]
        return latest_version, download_url

    elif program == "xz":
        url = "https://sourceforge.net/projects/lzmautils/files/"
        response = retry(requests.get, url, program=program, proxies=proxies)
        html = response.text
        match = re.search(r'xz-([0-9.]+)\.tar\.gz', html)
        if not match:
            raise ValueError(f"xz: 未找到版本号")
        latest_version = match.group(1)
        download_url = f"https://sourceforge.net/projects/lzmautils/files/xz-{latest_version}.tar.xz/download"
        return latest_version, download_url


    elif program == "sqlite":
        index_url = "https://www.sqlite.org/index.html"
        response = retry(requests.get, index_url, proxies=proxies)
        html = response.text
        version_match = re.search(r'>Version ([0-9.]+)<', html)
        if not version_match:
            return None, None
        latest_version = version_match.group(1)
        download_url = "https://www.sqlite.org/download.html"
        response = retry(requests.get, download_url, proxies=proxies)
        html = response.text
        csv_block = re.search(
            r'Download product data for scripts to read(.*?)-->', 
            html, 
            re.DOTALL
        )
        if csv_block:
            csv_data = csv_block.group(1)
            tarball_match = re.search(
                r'PRODUCT,[^,]*,\s*([^,]+sqlite-autoconf[^,]+\.tar\.gz)', 
                csv_data
            )
            if tarball_match:
                relative_path = tarball_match.group(1).strip()
                download_url = f"https://www.sqlite.org/{relative_path}"
                return latest_version, download_url
        return None, None


    else:
        raise ValueError(f"不支持的程序: {program}")

def fetch_program(program):
    current_version = current_versions[program]
    try:
        latest_version, download_url = get_latest_version(program, proxies=proxies)
        if latest_version is None or download_url is None:
            return program, current_version, None, None, "⚠️ 获取版本信息失败"
        if version.parse(latest_version) > version.parse(current_version):
            return program, current_version, latest_version, download_url, "🔴🔴 需更新"
        else:
            return program, current_version, latest_version, download_url, "已是最新版"
    except Exception as e:
        return program, cur_ver, None, None, f"❌ 获取失败: {str(e)[:80]}"

# ==========================
# 主调度 - 并发执行
# ==========================

results = []

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(fetch_program, prog): prog for prog in current_versions.keys()}
    for future in as_completed(futures):
        results.append(future.result())

# 按程序名字母顺序排序
results.sort(key=lambda x: x[0])

update_found = False
table = "| 程序 | 当前版本 | 最新版本 | 状态 | 下载地址 | 备注 |\n| --- | --- | --- | --- | --- | --- |\n"

for program, cur_ver, latest_ver, url, status in results:
    if status.startswith("🔴"):
        update_found = True
    if latest_ver and url:
        table += f"| {program} | {cur_ver} | {latest_ver} | {status} | [下载链接]({url}) | {program_environments.get(program, '通用')} |\n"
    else:
        table += f"| {program} | {cur_ver} | N/A | {status} | N/A | {program_environments.get(program, '通用')} |\n"

print(table)
if not update_found:
    print("- 检测结束，所有程序都没有更新的版本")
print("- 检测结束")
