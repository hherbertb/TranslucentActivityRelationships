import copy

from pandas import DataFrame
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureLog
from pm4py.objects.log.obj import EventLog, Trace
from pm4py.objects.dfg.obj import DFG
from typing import TypeVar, Generic, Optional, Union
from translucent_discovery.translucent_inductive_miner.tDFG import discover_dfg, discover_frequent_dfg
from pm4py.objects.dfg.obj import DFG
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL
import pm4py


def split_log(uvcl, log):
    variants = pm4py.statistics.variants.log.get.get_variants(log)
    variant_log = EventLog(attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                           omni_present=log.omni_present, properties=log.properties)
    for variant in variants:
        variant_log.append(variants[variant][0])
    new_log = EventLog(attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                           omni_present=log.omni_present, properties=log.properties)
    counter = 0
    for ref_trace in uvcl:
        if len(ref_trace) > 0:
            for index, trace in enumerate(variant_log):
                i = 0
                new_trace = Trace()
                for event in trace:
                    if event["concept:name"] == ref_trace[i]:
                        new_trace.append(event)
                        i += 1
                    if i >= len(ref_trace):
                        trace_to_append = copy.deepcopy(new_trace)
                        temp = trace.attributes["concept:name"]
                        temp = str(temp) +"_"+str(counter)
                        trace_to_append._set_attributes({"concept:name": temp})
                        new_log.append(copy.deepcopy(trace_to_append))
                        counter += 1
                        i = 0
                        new_trace = Trace()
        else:
            empty_trace = Trace()
            empty_trace._set_attributes({"concept:name":  "X_" + str(counter)})
            counter += 1
            new_log.append(copy.deepcopy(empty_trace))
    return new_log


class IMDataStructureTranslucent(IMDataStructureLog[UVCL]):
    def __init__(self, obj: UVCL, log, dfg: Optional[DFG] = None, frequent=False, tdfg = None):
        super().__init__(obj)
        if dfg is None:
            self._dfg = comut.discover_dfg_uvcl(self._obj)
        else:
            self._dfg = dfg
        self._frequent = frequent
        self._log = split_log(self._obj, copy.deepcopy(log))
        if not frequent:
            self._tdfg = discover_dfg(self._log)
        else:
            if tdfg is None:
                self._tdfg = discover_frequent_dfg(self._log)
            else:
                self._tdfg = tdfg

    @property
    def dfg(self) -> DFG:
        return self._dfg

    @property
    def tdfg(self) -> DFG:
        return self._tdfg

    @property
    def log(self):
        return self._log

    @property
    def frequent(self):
        return self._frequent

