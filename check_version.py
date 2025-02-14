import requests
import re
from packaging import version
import time
from bs4 import BeautifulSoup

# 配置代理 (根据需要修改)
proxies = {
    "http": "http://127.0.0.1:7788",  # 示例，根据你的实际代理设置修改
    "https": "https://127.0.0.1:7788", # 示例
}
proxies = None  # 不使用代理

# 定义当前版本
current_versions = {
    "zlib": "1.3.1",
    "zstd": "1.5.6",
    "gmp": "6.3.0",
    "isl": "0.27",
    "mpfr": "4.2.1",
    "mpc": "1.3.1",
    "binutils": "2.44",
    "gcc": "14.2.0",
    "nettle": "3.10.1",
    "libtasn1": "4.20.0",
    "libunistring": "1.3",
    "gpg-error": "1.51",
    "libassuan": "3.0.1",
    "gpgme": "1.24.2",
    "c-ares": "1.34.4",
    "libiconv": "1.18",
    "libidn2": "2.3.0",
    "libpsl": "0.21.5",
    "pcre2": "10.45",
    "expat": "2.6.4",
    "libmetalink": "0.1.3",
    "gnutls": "3.8.9",
    "nghttp2": "1.64.0",
    "libmicrohttpd": "1.0.1",
    "zlib-ng": "2.2.4",
    "libssh2": "1.11.1",
    "libxml2": "2.13.5",
    "xz": "5.6.4",
    "sqlite": "3.49.0",
}

# 重试函数 (支持代理) - **修改：移除 retry 内部的打印**
def retry(func, url, max_retries=5, delay=2, proxies=None, program=None):
    attempts = 0
    while attempts < max_retries:
        try:
            response = func(url, proxies=proxies)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            attempts += 1
            if attempts == max_retries: # 只在最终失败时才抛出异常，让外层循环的 except 块处理
                raise e
            time.sleep(delay)

# 获取最新版本的函数 (支持代理)
def get_latest_version(program, proxies=None):
    if program == "zlib":
        url = "https://api.github.com/repos/madler/zlib/releases/latest1"  # 故意使用错误的 URL 测试错误处理
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

    elif program == "libmetalink":
        url = "https://api.github.com/repos/metalink-dev/libmetalink/releases/latest"
        response = retry(requests.get, url, proxies=proxies,program=program)
        data = response.json()
        latest_version = data["tag_name"].lstrip("release-")
        download_url = data["assets"][0]["browser_download_url"]
        return latest_version, download_url

    elif program == "gnutls":
        base_url = "https://www.gnupg.org/ftp/gcrypt/gnutls/" # 返回到基础 URL 以列出版本
        response = retry(requests.get, base_url, proxies=proxies,program=program)
        version_dir_matches = re.findall(r'href="v([\d.]+)"', response.text) # 再次查找版本目录
        if not version_dir_matches:
            return current_versions["gnutls"], f"https://www.gnupg.org/ftp/gcrypt/gnutls/gnutls-{current_versions['gnutls']}.tar.xz"
        latest_version_dir = max(version_dir_matches, key=version.parse) # 获取最新的版本目录
        version_url = base_url + f"v{latest_version_dir}/" # 构建最新的版本目录的 URL
        version_response = retry(requests.get, version_url, proxies=proxies,program=program) # 获取最新的版本目录页面
        matches = re.findall(r'href="gnutls-([\d.]+)\.tar\.xz"', version_response.text) # 在最新的版本目录中查找 tar.xz 文件
        if not matches:
             return current_versions["gnutls"], f"https://www.gnupg.org/ftp/gcrypt/gnutls/gnutls-{current_versions['gnutls']}.tar.xz"
        latest_version = max(matches, key=version.parse) # Corrected max call with version.parse as key
        download_url = f"https://www.gnupg.org/ftp/gcrypt/gnutls/v{latest_version_dir}/gnutls-{latest_version}.tar.xz" # 使用最新的版本目录构建正确的 URL
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
        download_url = f"https://sourceforge.net/projects/lzmautils/files/xz-{latest_version}.tar.xz"
        return latest_version, download_url


    elif program == "sqlite":
        # 获取最新版本号
        index_url = "https://www.sqlite.org/index.html"
        response = retry(requests.get, index_url, proxies=proxies)
        html = response.text
        # 使用正则表达式提取版本号
        version_match = re.search(r'>Version ([0-9.]+)<', html)
        if not version_match:
            return None, None
        latest_version = version_match.group(1)

        # 获取下载页面内容
        download_url = "https://www.sqlite.org/download.html"
        response = retry(requests.get, download_url, proxies=proxies)
        html = response.text

        # 提取 CSV 数据部分
        csv_data = re.search(r'Download product data for scripts to read(.*?)-->', html, re.DOTALL)
        if not csv_data:
            return None, None

        # 提取 autoconf 的 tar.gz 文件链接
        tarball_match = re.search(r'autoconf.*?\.tar\.gz', csv_data.group(1))
        if not tarball_match:
            return None, None

        # 构建完整的下载链接
        tarball_url = tarball_match.group(0)
        download_url = f"https://www.sqlite.org/{tarball_url}"
        return latest_version, download_url


    else:
        raise ValueError(f"不支持的程序: {program}")

# 检查更新
update_found = False
error_messages = [] # 初始化错误消息列表

# 初始化表格头
table = "| 程序 | 当前版本 | 最新版本 | 状态 | 下载地址 |\n| --- | --- | --- | --- | --- |\n"

for program, current_version in current_versions.items():
    try:
        latest_version, download_url = get_latest_version(program, proxies=proxies)
        if latest_version is None or download_url is None:  # SQLite check
            error_messages.append(f"- {program}: 无法获取最新版本信息") # 添加错误消息到列表
            table += f"| {program} | {current_version} | N/A | ⚠️ 获取版本信息失败 | N/A |\n" # 添加错误状态到表格
            continue

        # 判断是否有新版本
        if version.parse(latest_version) > version.parse(current_version):
            table += f"| {program} | {current_version} | {latest_version} | 🔴 需更新 | [下载链接]({download_url}) |\n"
            update_found = True
        else:
            # 修正点：闭合大括号并移除多余符号
            table += f"| {program} | {current_version} | {latest_version} | 已是最新版 | [下载链接]({download_url}) |\n"

    except Exception as e:
        error_messages.append(f"- {program} 获取最新版本失败: {e}") # 添加错误消息到列表
        table += f"| {program} | {current_version} | N/A | ❌ 获取版本失败 | N/A |\n" # 添加错误状态到表格

# 先打印所有错误消息
if error_messages:
    print("--- 错误信息 ---")
    for msg in error_messages:
        print(msg)
    print("---")

# 打印带超链接的消息表格
print(table)

# 如果没有发现更新
if not update_found:
    print("- 检测结束，所有程序都没有更新的版本")
print("- ******检测结束******")
