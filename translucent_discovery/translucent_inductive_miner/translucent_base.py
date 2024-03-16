from translucent_discovery.translucent_inductive_miner.im import IM
from pm4py.util.compression import util as comut
from pm4py.util import xes_constants as xes_util
from enum import Enum
from pm4py.util import constants
from pm4py.util import exec_utils
from pm4py import util as pmutil
import pandas as pd
import pm4py
from translucent_discovery.translucent_inductive_miner.data_structure import IMDataStructureTranslucent
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


def discover_process_tree(log, parameters):
    ack = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    tk = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY)
    cidk = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, pmutil.constants.CASE_CONCEPT_NAME)
    if isinstance(log, pd.DataFrame):
        log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)
    uvcl = comut.get_variants(comut.project_univariate(log, key=ack, df_glue=cidk, df_sorting_criterion_key=tk))
    im = IM(parameters)
    temp = IMDataStructureTranslucent(uvcl, log)
    return im.apply(temp, parameters)


def discover_petri_net(log, parameters):
    process_tree = discover_process_tree(log, parameters)
    return pm4py.convert_to_petri_net(process_tree)

