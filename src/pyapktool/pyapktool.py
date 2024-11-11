import requests
import argparse
import os
import json
import pathlib
import subprocess


tools_dir = "pyapktool_tools"


def print_ok(message):
    print(f"\033[92m[+]{message}\033[0m")  # \033[92m is the ANSI code for green

def print_error(message):
    print(f"\033[91m[-]{message}\033[0m")  # \033[91m is the ANSI code for red


class GitHubAssetUpdater:
    def __init__(self, output_dir, asset_path, release_url):
        self.output_dir = output_dir
        self.asset_path = asset_path
        self.release_url = release_url

    def __download_asset(self, asset):
        os.makedirs(self.output_dir, exist_ok=True)
        print_ok(f"Downloading {asset['name']} to {self.output_dir}...")
        response = requests.get(asset["browser_download_url"], stream=True)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print_error(f"Failed downloading {asset['name']}")
            raise e

        with open(self.asset_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print_ok(f"Downloaded {asset['name']} to {self.asset_path}")

    def download_github_asset(self):
        print_ok(f"Trying to download latest release from {self.release_url}")
        asset_ext = pathlib.Path(self.asset_path).suffix
        release_response = json.loads(requests.get(self.release_url).content)
        assets_url = release_response["assets_url"]
        assets_response = json.loads(requests.get(assets_url).content)
        for asset in assets_response:
            if asset["name"].endswith(asset_ext):
                self.__download_asset(asset)
                break


class BaseTool:
    def __init__(self, output_dir, tool_name, github_release_url):
        self.java_path = self.__get_java_path()
        self.output_dir = output_dir
        self.tool_name = tool_name
        self.tool_path = os.path.abspath(os.path.join(self.output_dir, self.tool_name))
        self.github_asset_updater = GitHubAssetUpdater(self.output_dir, self.tool_path, github_release_url)

    def is_tool_exists(self):
        if os.path.isfile(self.tool_path):
            print_ok(f"{self.tool_name} already exists at: {self.tool_path}. Skipping download")
            return True

        return False

    def _get_tool(self):
        if not self.is_tool_exists():
            self.github_asset_updater.download_github_asset()

        return self.tool_path

    def __get_java_path(self):
        java_path = "java.exe"

        # Check if JAVA_HOME is defined in the environment variables
        if "JAVA_HOME" in os.environ:
            java_path = os.path.join(os.environ["JAVA_HOME"], "bin", "java.exe")

        try:
            # check if java exists
            subprocess.run([java_path, "-version"], capture_output=True, text=True, check=True)
        except Exception as e:
            raise f"Java not found on {java_path}. Make sure it's available and then run this script again.\nError: {e}"

        return java_path


class Apktool(BaseTool):
    github_release_url = "https://api.github.com/repos/iBotPeaches/Apktool/releases/latest"
    apktool = "apktool.jar"

    def __init__(self, output_dir):
        super().__init__(output_dir, Apktool.apktool, Apktool.github_release_url)
        self.apktool_path = None

    def get(self):
        self.apktool_path = super()._get_tool()

    def pack(self, target_path):
        print_ok(f"Trying to pack {target_path} into APK")
        output_path = os.path.join(target_path, "dist")
        apk_output = os.path.join(output_path, pathlib.Path(target_path).name + ".apk")

        try:
            p = subprocess.run([self.java_path, "-jar", "-Duser.language=en", "-Dfile.encoding=UTF8",
                                self.apktool_path, "b", target_path], capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print_error(f"Error {e.returncode}: {e.stderr}\nFailed to pack {target_path} into APK")
            return

        if p.stderr:
            print_error(f"Error: {p.returncode}: {p.stderr}\nFailed to pack {target_path} into APK")
            return

        print_ok(f"APK packed successfully at {apk_output}")
        return apk_output

    def unpack(self, target_path, output_path=None):
        print_ok(f"Trying to unpack {target_path}")
        if not output_path:
            output_path = os.path.splitext(target_path)[0]
        else:
            output_path = os.path.abspath(output_path)

        try:
            p = subprocess.run([self.java_path, "-jar", "-Duser.language=en", "-Dfile.encoding=UTF8",
                            self.apktool_path, "d", target_path, "-o", output_path], capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print_error(f"Error: {e.returncode}: {e.stderr}\nFailed to unpack {target_path}")
            return

        if p.stderr:
            print_error(f"Error: {p.returncode}: {p.stderr}\nFailed to unpack {target_path}")
            return

        print_ok(f"APK was unpacked successfully into {output_path}")


class ApkSigner(BaseTool):
    github_release_url = "https://api.github.com/repos/patrickfav/uber-apk-signer/releases/latest"
    signer = "apk-signer.jar"

    def __init__(self, output_dir):
        super().__init__(output_dir, ApkSigner.signer, ApkSigner.github_release_url)
        self.signer_path = None

    def get(self):
        self.signer_path = super()._get_tool()

    def sign(self, apk_path, delete_idsig_file=True):
        print_ok(f"Trying to sign {apk_path} with debug keys")
        apk_signed_path = os.path.abspath(f"{pathlib.Path(apk_path).stem}-signed.apk")

        try:
            p = subprocess.run([self.java_path, "-jar", self.signer_path, "-a", apk_path, "-o", os.getcwd()], capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print_error(f"Error {e.returncode}: {e.stderr}\nFailed to sign {apk_path}")
            return

        if p.stderr:
            print_error(f"Error: {p.returncode}: {p.stderr}\nFailed to sign {apk_path}")
            return

        # finding the signed apk in CWD and renaming to {apk_signed_path}. the apk-signer output apk usually ends with "<name>Signed.apk"
        signed_output = None
        for f in os.listdir(os.getcwd()):
            if f.endswith("Signed.apk"):
                signed_output = f
            elif delete_idsig_file and f.endswith(".apk.idsig"):
                # by default, will try to delete the idsig file which is generated as a byproduct of the signing process
                os.remove(f)

        if not signed_output:
            print_error(f"Error: Couldn't find signed apk in current working directory. Maybe the signing process failed.")
            return

        os.replace(signed_output, apk_signed_path)
        print_ok(f"APK packed and signed successfully at {apk_signed_path}")


def pack_and_sign_apk(target_path):
    print_ok("Downloading required tools")
    apktool = Apktool(tools_dir)
    apktool.get()
    apk_signer = ApkSigner(tools_dir)
    apk_signer.get()

    apk_output = apktool.pack(target_path)
    apk_signer.sign(apk_output)


def unpack_apk(target_path):
    print_ok("Downloading required tools")
    apktool = Apktool(tools_dir)
    apktool.get()

    apktool.unpack(target_path)


def get_args():
    parser = argparse.ArgumentParser(description="Unpack/Pack apk and sign it")
    parser.add_argument("target", type=str, help="A path to an apk to unpack OR A path to an unpacked directory to pack into apk and sign it")
    return parser.parse_args()


def init(target):
    if os.path.isdir(target):
        print_ok(f"Packing {target} into an APK and signing it")
        return pack_and_sign_apk
    elif os.path.isfile(target) and pathlib.Path(target).suffix == ".apk":
        print_ok(f"Unpacking {target}")
        return unpack_apk

    print_error(f"{target} not recognized as a path to an apk or a directory to pack")


def main():
    args = get_args()
    target_path = os.path.abspath(args.target)
    action = init(target_path)
    if not action:
        return

    action(target_path)



if __name__ == '__main__':
    main()



