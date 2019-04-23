"""Set of helper functions for pyATS and Genie.

Used in other scripts to easily retrieve Genie Ops objects and devices.

ToDo:
- Update and simplify with new .learn() syntax

"""


# from ats.topology import loader
# from genie.conf import Genie
from genie.abstract import Lookup
from genie.libs import ops
from genie.conf import Genie

# from genie import parsergen


def load_testbed(testbed):
    genie_testbed = Genie.init(testbed)
    return genie_testbed


def genie_prep(dev):
    """
    Connects and looks up platform parsers for device
    Returns an abstract object
    """
    # Device must be connected so that a lookup can be performed
    if not dev.is_connected():
        dev.connect()

    # Load the approprate platform parsers dynamically
    abstract = Lookup.from_device(dev)
    return abstract


def get_platform_info(dev):
    """
    Returns parsed and normalized platform details
    https://pubhub.devnetcloud.com/media/pyats-packages/docs/genie/genie_libs/#/models/platform
    """
    abstract = genie_prep(dev)

    # Find the Platform Parsers for this device
    parse = abstract.ops.platform.platform.Platform(dev)

    # Parse required commands, and return structured data
    parse.learn()

    # See if the software version is in the model, if not fix
    try:
        parse.version
    except AttributeError:
        sh_ver = dev.parse("show version")
        if parse.os == "NX-OS":
            parse.version = sh_ver["platform"]["software"]["system_version"]

    return parse


def get_interfaces(dev):
    """
    Returns parsed and normalized interface details
    https://pubhub.devnetcloud.com/media/pyats-packages/docs/genie/genie_libs/#/models/interface
    """
    abstract = genie_prep(dev)

    # Find the Interface Parsers for this device
    parse = abstract.ops.interface.interface.Interface(dev)

    # Parse required commands, and return structured data
    parse.learn()
    return parse.info
