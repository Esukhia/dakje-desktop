# coding:utf8
import sys
import subprocess


if __name__ == "__main__":

    # Check Python version
    print('Checking your system ...')
    print("Python Version: {0:d}.{1:d}.{2:d}".format(*sys.version_info[:3]))
    if sys.version_info < (3, 5, 0) and sys.version_info[0] == 3:
        print("Sorry, you must have Python 3.5.0 or higher.")
        exit(5)

    # upgrade pip
    subprocess.call(
        [sys.executable, "-m", "pip", "install", "pip", "--user", "--upgrade"]
    )

    # upgrade setuptools
    subprocess.call(
        [sys.executable, "-m", "pip", "install", "setuptools", "--user", "--upgrade"]
    )
    print()

    # get dependencies
    print('Installing Dakje ...')
    subprocess.call(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--user", "--upgrade"]
    )


    from shortcut import ShortCutter
    s = ShortCutter()
    s.create_desktop_shortcut("Dakje.pyw")
    s.create_menu_shortcut("Dakje.pyw")

    print()
    print('Done!')
    print()
