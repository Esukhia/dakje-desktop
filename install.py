# coding:utf8
import sys
import subprocess


if __name__ == "__main__":
    print('Preparing Dakje ...')
    subprocess.call(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--user", "--upgrade"]
    )
    print('Done!')
    print()
