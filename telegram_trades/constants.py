from toolkit.fileutils import Fileutils
from toolkit.logger import Logger
from toolkit.utilities import Utilities

logging = Logger(10)
DIRP = "../../"
DATA = "../data/"
FUTL = Fileutils()
SETG = FUTL.get_lst_fm_yml(DIRP + "ravikanth.yml")
BRKR = SETG["aliceblue"]
logging.debug(BRKR)
TGRM = SETG["telegram"]
logging.debug(TGRM)
CHANNEL_DETAILS = SETG["channel_details"]
UTIL = Utilities()
