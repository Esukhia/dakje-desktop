# coding:utf8
import sys
import subprocess

# Adapted from Eric IDE's install.py script

def pip_install(package_name, message):
    """
    Install the given package via pip.

    @param package_name name of the package to be installed
    @type str
    @param message message to be shown to the user
    @type str
    @return flag indicating a successful installation
    @rtype bool
    """
    ok = False

    print(
        "{0}\n\n'{1}' will be installed.".format(
            message, package_name
        )
    )
    exit_code = subprocess.call(
        [sys.executable, "-m", "pip", "install", package_name]
    )
    ok = exit_code == 0

    return ok


def do_dependency_checks():
    """
    Perform some dependency checks for PyQt5 and PyQt5-sip
    """
    print("Checking dependencies")

    # perform dependency checks
    print("Python Version: {0:d}.{1:d}.{2:d}".format(*sys.version_info[:3]))
    if sys.version_info < (3, 5, 0) and sys.version_info[0] == 3:
        print("Sorry, you must have Python 3.5.0 or higher.")
        exit(5)
    print()

    ##########################################################
    # PyQt5
    ##########################################################

    try:
        from PyQt5.QtCore import qVersion
    except ImportError as msg:
        if sys.version_info[0] == 2:
            # no PyQt5 wheels available for Python 2
            installed = False
        else:
            installed = pip_install(
                "PyQt5==5.11.3", "PyQt5 could not be detected.\nError: {0}".format(msg)
            )
        if installed:
            # try to import it again
            try:
                from PyQt5.QtCore import qVersion
            except ImportError as msg:
                print("Sorry, please install PyQt5.")
                print("Error: {0}".format(msg))
                exit(1)
        else:
            print("Sorry, please install PyQt5.")
            print("Error: {0}".format(msg))
            exit(1)
    print("Found PyQt5")

    # check version of Qt
    qtMajor = int(qVersion().split(".")[0])
    qtMinor = int(qVersion().split(".")[1])
    print("\tQt Version: {0}".format(qVersion().strip()))
    if qtMajor < 4 or (qtMajor == 4 and qtMinor < 8) or (qtMajor == 5 and qtMinor < 9):
        print("Sorry, you must have Qt version 4.8.0 or better or")
        print("5.9.0 or better.")
        exit(2)

    ##########################################################
    # PyQt5-sip
    ##########################################################
    try:
        try:
            from PyQt5 import sip
        except ImportError as msg:
            installed = pip_install(
                "PyQt5", "PyQt5 could not be detected.\nError: {0}".format(msg)
            )
            if installed:
                # try to import it again
                try:
                    from PyQt5 import sip
                except ImportError as msg:
                    print("Sorry, please install PyQt5.")
                    print("Error: {0}".format(msg))
                    exit(1)
            else:
                print("Sorry, please install PyQt5.")
                print("Error: {0}".format(msg))
                exit(1)
        print("Found PyQt5-sip")

        # check version of sip
        sipVersion = sip.SIP_VERSION_STR
        print("\tsip Version:", sipVersion.strip())
        # always assume, that snapshots or dev versions are new enough
        if "snapshot" not in sipVersion and "dev" not in sipVersion:
            while sipVersion.count(".") < 2:
                sipVersion += ".0"
            (major, minor, pat) = sipVersion.split(".")
            major = int(major)
            minor = int(minor)
            pat = int(pat)
            if (
                major < 4
                or (major == 4 and minor < 14)
                or (major == 4 and minor == 14 and pat < 2)
            ):
                print(
                    "Sorry, you must have sip 4.14.2 or higher or"
                    " a recent snapshot release."
                )
                exit(3)
    except (ImportError, AttributeError):
        pass

    ##########################################################
    # appdirs
    ##########################################################
    try:
        import appdirs
    except ImportError as msg:
        installed = pip_install(
            "appdirs==1.4.3", "Appdirs could not be detected.\nError: {0}".format(msg)
        )

        if installed:
            # try to import it again
            try:
                import appdirs
            except ImportError as msg:
                print("Sorry, please install appdirs.")
                print("Error: {0}".format(msg))
                exit(1)
        else:
            print("Sorry, please install appdirs.")
            print("Error: {0}".format(msg))
            exit(1)
    print("Found appdirs")

    # not checking appdirs version

    ##########################################################
    # pybo
    ##########################################################
    try:
        import pybo
    except ImportError as msg:
        installed = pip_install(
            "pybo==0.2.21", "pybo could not be detected.\nError: {0}".format(msg)
        )

        if installed:
            # try to import it again
            try:
                import pybo
            except ImportError as msg:
                print("Sorry, please install pybo.")
                print("Error: {0}".format(msg))
                exit(1)
        else:
            print("Sorry, please install pybo.")
            print("Error: {0}".format(msg))
            exit(1)
    print("Found pybo")

    # not checking pybo version


    ##########################################################
    # PyYAML
    ##########################################################
    try:
        import yaml
    except ImportError as msg:
        print(msg)
        installed = pip_install(
            "PyYAML==3.13", "PyYAML could not be detected.\nError: {0}".format(msg)
        )

        if installed:
            # try to import it again
            try:
                import yaml
            except ImportError as msg:
                print("Sorry, please install PyYAML.")
                print("Error: {0}".format(msg))
                exit(1)
        else:
            print("Sorry, please install PyYAML.")
            print("Error: {0}".format(msg))
            exit(1)
    print("Found PyYAML")

    # not checking PyYAML version



    ##########################################################
    # experta
    ##########################################################
    try:
        import experta
    except ImportError as msg:
        installed = pip_install(
            "experta", "experta could not be detected.\nError: {0}".format(msg)
        )

        if installed:
            # try to import it again
            try:
                import experta
            except ImportError as msg:
                print("Sorry, please install experta.")
                print("Error: {0}".format(msg))
                exit(1)
        else:
            print("Sorry, please install experta.")
            print("Error: {0}".format(msg))
            exit(1)
    print("Found experta")

    # not checking experta version

    ##########################################################
    # Django
    ##########################################################
    try:
        import django
    except ImportError as msg:
        installed = pip_install(
            "Django>=1.11,<2", "Django could not be detected.\nError: {0}".format(msg)
        )

        if installed:
            # try to import it again
            try:
                import django
            except ImportError as msg:
                print("Sorry, please install Django.")
                print("Error: {0}".format(msg))
                exit(1)
        else:
            print("Sorry, please install Django.")
            print("Error: {0}".format(msg))
            exit(1)
    print("Found Django")

    # not checking Django version


    print()
    print("All set!")



if __name__ == "__main__":
    do_dependency_checks()
