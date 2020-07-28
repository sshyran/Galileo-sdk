import sys

if sys.version_info[0] == 3:
    from .events import GalileoConnector

from .repositories import (
    JobsRepository,
    LzRepository,
    ProfilesRepository,
    MissionsRepository,
    RequestsRespository,
    StationsRepository,
    SettingsRepository,
)
from .providers import AuthProvider
# from .util import file_dict_to_file_listing, job_dict_to_job
