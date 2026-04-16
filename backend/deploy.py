import os
import shutil
import zipfile
import subprocess


def _docker_volume_args():
    return [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{os.getcwd()}:/var/task",
        "--platform",
        "linux/amd64",
        "--entrypoint",
        "",
        "public.ecr.aws/lambda/python:3.12",
    ]


def remove_lambda_package():
    """Remove lambda-package; use Docker if root-owned (e.g. prior Docker pip on /mnt/c in WSL)."""
    if not os.path.exists("lambda-package"):
        return
    try:
        shutil.rmtree("lambda-package")
    except PermissionError:
        print("Removing root-owned lambda-package via Docker...")
        subprocess.run(
            _docker_volume_args()
            + ["/bin/sh", "-c", "rm -rf /var/task/lambda-package"],
            check=True,
        )


def main():
    print("Creating Lambda deployment package...")

    # Clean up (Docker-created trees may not be deletable on /mnt/c from WSL)
    remove_lambda_package()
    if os.path.exists("lambda-deployment.zip"):
        try:
            os.remove("lambda-deployment.zip")
        except PermissionError:
            subprocess.run(
                _docker_volume_args()
                + ["/bin/sh", "-c", "rm -f /var/task/lambda-deployment.zip"],
                check=True,
            )

    # Create package directory
    os.makedirs("lambda-package")

    # Install dependencies using Docker with Lambda runtime image
    print("Installing dependencies for Lambda runtime...")

    # Match host UID/GID on Unix so files on shared volumes (e.g. /mnt/c in WSL) are not root-only.
    user_args = (
        ["-u", f"{os.getuid()}:{os.getgid()}"]
        if hasattr(os, "getuid") and hasattr(os, "getgid")
        else []
    )

    # Use the official AWS Lambda Python 3.12 image
    # This ensures compatibility with Lambda's runtime environment
    subprocess.run(
        _docker_volume_args()[:2]  # docker, run
        + user_args
        + _docker_volume_args()[2:]  # --rm -v ... image
        + [
            "/bin/sh",
            "-c",
            "pip install --target /var/task/lambda-package -r /var/task/requirements.txt --platform manylinux2014_x86_64 --only-binary=:all: --upgrade",
        ],
        check=True,
    )

    # Copy application files
    print("Copying application files...")
    for file in ["server.py", "lambda_handler.py", "context.py", "resources.py"]:
        if os.path.exists(file):
            shutil.copy2(file, "lambda-package/")
    
    # Copy data directory
    if os.path.exists("data"):
        shutil.copytree("data", "lambda-package/data")

    # Create zip
    print("Creating zip file...")
    with zipfile.ZipFile("lambda-deployment.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("lambda-package"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, "lambda-package")
                zipf.write(file_path, arcname)

    # Show package size
    size_mb = os.path.getsize("lambda-deployment.zip") / (1024 * 1024)
    print(f"✓ Created lambda-deployment.zip ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()