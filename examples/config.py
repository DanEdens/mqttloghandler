import argparse
import inspect
import os
import re
import subprocess
import sys
from datetime import datetime
from datetime import timedelta

from dvttestkit import testKitUtils

from OculusTestKit.decorators import singleton


def list_classes_in_module(module):
    """
    List all classes defined in the current module.
    """
    return [name for name, obj in inspect.getmembers(module, inspect.isclass)
            if obj.__module__ == module.__name__]


@singleton
class OculusTestKit:

    def __init__(self):
        """
        Initialize the RegressionTestKit with optional settings.
        """
        self.logger = self.logger_setup()
        self.env = self.arg_setup()

        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv("RTK_BQ_KEY", "em-beta*.json")
        if self.env.verbose:
            self.logger.setLevel(5)
            self.logger.debug("Overriding log level to VERBOSE")
        elif self.env.debug:
            self.logger.setLevel("DEBUG")
            self.logger.debug("Overriding log level to DEBUG")

    @staticmethod
    def logger_setup():
        """
        Sets up the logger for the OculusTestKit.

        :returns: Configured logger instance.
        :rtype: logging.Logger
        """
        return testKitUtils.makeLogger(name=f'OTK/{os.getenv("BITBUCKET_REPO_SLUG", "local")}/log',
                                       log_level=os.getenv("OTK_DEBUG", "INFO"))

    def arg_setup(self, description: str = "Shared Oculus toolkit for Elemental Machines Test automation."):
        """
        Parse command line arguments.

        :returns: Parsed command line arguments.
        :rtype: argparse.Namespace
        """
        if not any(module in sys.modules for module in ["sphinx", "pytest"]):
            def _parse_args():
                parser = argparse.ArgumentParser(
                    description=description,
                    prog=self.__class__.__name__,
                    formatter_class=argparse.RawDescriptionHelpFormatter
                )
                parser.add_argument("-a", "--auto", action="store_true",
                                    default=os.getenv("RTK_AGENT_MODE", False),
                                    help="(bool) Enables Agent mode. This flag is for pipeline jobs and skips user prompting."
                                    )
                parser.add_argument("-u", "--uuid", type=str,
                                    default=os.getenv("RTK_UUID"),
                                    help="(str): Gateway DUT UUID. Default is RTK_UUID. "
                                         "EX. c9e3b8b3b3b3b3b3b3b3b3b3b3b3b3b"
                                    )
                parser.add_argument("--fleet", type=str,
                                    default=os.getenv("RTK_FLEET"),
                                    help="(str) Fleet of gateways to query against. Default is the value of RTK_FLEET."
                                    )
                parser.add_argument("--sensor_list", type=str, nargs='+',
                                    help="(list): List of sensor mac addresses to query against. Default is None."
                                    )
                parser.add_argument("--output", type=str,
                                    default=os.getenv("RTK_OUTPUT", "data"),
                                    help="(str): Output folder path. Defaults to 'data/'"
                                    )
                parser.add_argument("--retest", type=str,
                                    default=os.getenv("RTK_RETEST", "tests/retest"),
                                    help="(str): Output file name for retest lists. Default is 'tests/retest'."
                                    )
                parser.add_argument("--ticket", type=str,
                                    default=os.getenv("RTK_TICKET"),
                                    help="(str): JIRA ticket number. Default is the value of the environment variable."
                                         "RTK_TICKET. EX. 'TDV-1234'."
                                    )
                parser.add_argument("--file", type=str,
                                    default=os.getenv("RTK_FILE"),
                                    help="(str): Various functions use this for input file names, "
                                         "Whitelist by default"
                                    )
                parser.add_argument("--pubkey", type=str,
                                    default=os.getenv("RTK_PNPK"),
                                    help="(str): PubNub publish key. Default is the value of the "
                                         "environment variable PUBNUB_PUBLISH_KEY."
                                    )
                parser.add_argument("--subkey", type=str,
                                    default=os.getenv("RTK_PNSK"),
                                    help="(str): PubNub subscribe key. Default is the value of the "
                                         "environment variable PUBNUB_SUBSCRIBE_KEY."
                                    )
                parser.add_argument("--until", type=str,
                                    default=self.poll_date(),
                                    help="(str): End date for query. Default is the current date and time."
                                    )
                parser.add_argument("--debug", action="store_true",
                                    default=os.getenv("RTK_DEBUG", False),
                                    help="Enable debug mode."
                                    )
                parser.add_argument("-v", "--verbose", action="store_true",
                                    default=False,
                                    help="Enable verbose mode."
                                    )
                parser.add_argument("--host", type=str,
                                    default=os.getenv("RTK_HOST", "localhost"),
                                    help="(str): Host to connect to. Default is the value of the environment variable "
                                         "RTK_HOST."
                                    )
                parser.add_argument("--port", type=int,
                                    default=os.getenv("RTK_PORT", 8080),
                                    help="(int): Port to connect to. Default is the value of the environment variable "
                                         "RTK_PORT."
                                    )
                parser.add_argument("--show", action="store_true",
                                    default=False,
                                    help="(Show the test case in a browser."
                                    )
                parser.add_argument("--mode", type=str,
                                    default=os.getenv("RTK_MODE", "local"),
                                    help="(str): Mode to run in. Default is the value "
                                         "of the environment variable RTK_MODE."
                                    )
                parser.add_argument("--id", type=int,
                                    default=os.getenv("RTK_ID", -1),
                                    help="(int): Test monitor object ID. Default is the value of the environment variable RTK_ID."
                                    )
                parser.add_argument("--tr-id", type=int,
                                    dest="tr_id",
                                    default=os.getenv("RTK_TR_ID", -1),
                                    help="(int): Test run ID. Default is the value of the environment variable RTK_TC_ID."
                                    )
                parser.add_argument("--tc-id", type=int,
                                    dest="tc_id",
                                    default=os.getenv("RTK_TC_ID", -1),
                                    help="(int): Test case ID. Default is the value of the environment variable RTK_TC_ID."
                                    )
                parser.add_argument("-m", "--milestone", type=int,
                                    default=os.getenv("RTK_MILESTONE", -1),
                                    help="(int): Milestone ID. Default is the value of the environment variable RTK_MILESTONE."
                                    )
                parser.add_argument("-d", "--desc", type=str,
                                    help="(str): Description of the test case."
                                    )
                parser.add_argument("--status", type=int,
                                    default=1,
                                    dest="test_result_status_id",
                                    choices=[1, 2, 3, 4, 5],
                                    help="(int): When using CLI to update test results, This will mark the status as failed."
                                    )
                parser.add_argument("--skip_time", type=int,
                                    default=os.getenv("RTK_SKIP_TIME", 99),
                                    help="(int): Default Time to skip tests before rerunning them in hours. Default is 99."
                                    )
                parser.add_argument("--cli", action="store_true",
                                    default=False,
                                    help="(bool) Enable CLI mode."
                                    )
                parser.add_argument("--push", action="store_true",
                                    default=False,
                                    dest="push_on_exit",
                                    help="(bool) Push the object to the server on exit."
                                    )
                # selector
                group = parser.add_mutually_exclusive_group()
                current_module = sys.modules[__name__]
                print(sys.modules[__name__])
                classes = list_classes_in_module(current_module)
                for cls in classes:
                    group.add_argument(f'--{cls.lower()}', action='store_true', help=f'(bool) Run {cls}')
                group.add_argument('selector', type=str, nargs='?', default=None, help='(str) The class name or command to run')

                return parser.parse_args()

            return _parse_args()
        else:
            class MockThreadArgs:
                """
                This is necessary because Sphinx cannot run argparse in the documentation build process.

                This class is used to mimic the structure and attributes of the argparse.Namespace
                object returned by _parse_args(), without actually running argparse.
                """

                def __init__(self, auto=None, debug=None, file=None, tr_id=None, fleet=None, cli=None,
                             selector=None, retest=None, output=None, ticket=None, pubkey=None, subkey=None,
                             until=self.poll_date(), uuid=None, verbose=None, mode=None,
                             host=None, port=None, id=None, sensor_list=None, skip_time=None, description=None,
                             milestone=None):
                    self.auto = auto or os.getenv("RTK_AGENT_MODE", False)
                    self.cli = cli or False

                    self.uuid = uuid or os.getenv("RTK_UUID", None)
                    self.fleet = fleet or os.getenv("RTK_FLEET", 'g_brett_byer/reg_uart-dfu_gateway-3')
                    self.sensor_list = sensor_list
                    self.output = output or os.getenv("RTK_OUTPUT", "data")
                    self.retest = retest or os.getenv("RTK_RETEST", "tests/retest")
                    self.ticket = ticket or os.getenv("RTK_TICKET", "TDV-7")
                    self.file = file or os.getenv("RTK_FILE", 'whitelist.txt')
                    self.pubkey = pubkey or os.getenv("RTK_PNPK")
                    self.subkey = subkey or os.getenv("RTK_PNSK")
                    self.until = until
                    self.debug = debug or os.getenv("DVT_DEBUG", "INFO")
                    self.verbose = verbose or os.getenv("RTK_VERBOSE", False)
                    self.host = host or "localhost"
                    self.milestone = milestone or -1
                    self.port = port or 8080
                    self.push_on_exit = False
                    self.desc = description or None
                    self.show = False
                    self.mode = mode or "local"
                    self.id = id or os.getenv("RTK_ID")
                    self.selector = selector or None
                    self.tr_id = tr_id or os.getenv("RTK_TR_ID")
                    self.tc_id = id or os.getenv("RTK_TC_ID")
                    self.skip_time = skip_time or 4

            return MockThreadArgs()

    def poll_date(self, time_hours: int = None):
        """
        Returns a datetime.datetime that is {time_hours} from now.

        :param time_hours: The number of hours to poll the date for. Default is 0.
        :type time_hours: int
        """
        if time_hours is None:
            try:
                time_hours = int(os.getenv("RTK_POLL_UNTIL", 24))
            except ValueError:
                raise ValueError("RTK_POLL_UNTIL environment variable must be an integer.")
        # if time_hours is 0, return current time + 2 seconds
        if time_hours == 0:
            return datetime.now() + timedelta(seconds=2)
        else:
            return datetime.now() + timedelta(hours=int(time_hours))


_thread = OculusTestKit()
logger = _thread.logger


@singleton
class EnvData:
    """
    Singleton class to store environment variables.
    """

    def __init__(self):
        self.env = OculusTestKit().env

        self.auto: str = self.env.auto
        self.balena_version: str = subprocess.check_output(["balena", "--version"]).decode("utf-8").strip()
        self.cli: bool = self.env.cli
        self.debug: bool = self.env.debug
        self.description: str = self.env.desc or None
        self.file: str = self.env.file
        self.fleet: str = self.env.fleet
        self.host: str = self.env.host
        self.id: int = self.env.id
        self.milestone: int = self.env.milestone
        self.mode: str = self.env.mode
        self.node: str = os.uname().nodename
        self.output: str = self.env.output
        self.platform: str = os.uname().version
        self.port: int = self.env.port
        self.previous_version_commit: str | None = None
        self.previous_version: str | None = None
        self.pubkey: str = self.env.pubkey
        self.push_on_exit = self.env.push_on_exit
        self.python_version: str = sys.version
        self.retest: str = self.env.retest
        self.selector: str = self.env.selector
        self.sensor_list: list = self.env.sensor_list
        self.show: bool = self.env.show
        self.skip_time: int = self.env.skip_time
        self.subkey: str = self.env.subkey
        self.target_version_commit: str | None = None
        self.target_version: str | None = None
        self.tc_id: int = self.env.tc_id
        self.test_list: list | None = None
        self.test_result_status_id: int = 1
        self.tester: str = os.getenv('RTK_BALENA_USER', os.getenv('USER', 'Unknown'))
        self.ticket: str = self.env.ticket
        self.tr_id: int = self.env.tr_id
        self.until: datetime = self.env.until
        self.uuid: str = self.env.uuid
        self.verbose: bool = self.env.verbose

    def update(self, **kwargs):
        """Update attributes dynamically."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    @property
    def valid_uuid(self) -> str:
        """
        Validates a UUID string.

        :returns: The validated UUID string, or None if invalid.
        :rtype: str or None.
        """
        # return bool(re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac_address))

        if self.uuid is not None:
            if re.match(r'^[0-9a-f]{32}$', self.uuid) is not None:
                return self.uuid
            raise ValueError(f'UUID <{self.uuid}> is not in a valid format!')
