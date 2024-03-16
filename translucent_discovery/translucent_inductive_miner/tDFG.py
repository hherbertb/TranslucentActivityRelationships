import pandas as pd
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.dfg.obj import DFG
import pm4py
from translucent_discovery.utils.translucent_activity_relationships import get_parallel_relationships, \
    get_directly_follow_relationships, get_start_activities, get_end_activities


def discover_dfg(log) -> DFG:
    if isinstance(log, pd.DataFrame):
        log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)
    dfg = DFG()
    executed_activities = set()
    variants = pm4py.statistics.variants.log.get.get_variants(log)
    for variant in variants:
        trace = variants[variant][0]
        for event in trace:
            executed_activities.add(event["concept:name"])
    parallel = get_parallel_relationships(log, executed_activities)
    for source in parallel:
        for target in parallel[source]:
            dfg.graph.update({(source, target): 1})
    directly_follow = get_directly_follow_relationships(log, executed_activities)
    for source in directly_follow:
        for target in directly_follow[source]:
            dfg.graph.update({(source, target): 1})
    start_activities = get_start_activities(log, executed_activities)
    for act in start_activities:
        dfg.start_activities.update(({act: 1}))
    end_activities = get_end_activities(log, executed_activities)
    for act in end_activities:
        dfg.end_activities.update({act: 1})
    return dfg
