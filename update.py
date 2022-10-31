import pathlib
import re
import subprocess
import json


def get_image_digest(image_tag: str) -> str:
    output = subprocess.check_output(
        ["docker", "manifest", "inspect", image_tag, "-v"],
        stderr=subprocess.PIPE
    )
    result = json.loads(output)
    # There are at least two possible formats
    if isinstance(result, list) and len(result) > 0:
        for manifest in result:
            platform = manifest.get("Descriptor", {}).get("platform", {}).get("architecture")
            system = manifest.get("Descriptor", {}).get("platform", {}).get("os")
            if platform == "amd64" and system == "linux":
                return manifest["Descriptor"]["digest"]
    elif isinstance(result, dict):
        config_digest = result.get("Descriptor", {}).get("digest")
        if config_digest:
            return config_digest
    raise Exception(f"{image_tag} digest not found!\n{output.decode('utf-8')}")

    
def update():
    content = pathlib.Path(".devcontainer/devcontainer.json").read_text("utf-8")
    repo, original_digest = re.search(r"image\":\s*\"([^\"]+)\"", content).group(1).split("@")
    desired_digest = get_image_digest(repo + ":latest")
    content = content.replace(original_digest, desired_digest)
    pathlib.Path(".devcontainer/devcontainer.json").write_text(content, "utf-8")


if __name__ == "__main__":
    update()
