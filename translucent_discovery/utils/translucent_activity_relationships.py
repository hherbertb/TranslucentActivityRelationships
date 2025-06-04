from pm4py.objects.log.obj import EventLog
from pm4py.objects.conversion.log import converter as log_converter
import pandas as pd
import pm4py


def get_start_activities(log, executed_activities, enabled_activities_key="enabled_activities"):
    start_activities = set()
    variants = pm4py.statistics.variants.log.get.get_variants(log)
    for variant in variants:
        trace = variants[variant][0]
        if len(trace) > 0:
            start_activities_strings = trace[0][enabled_activities_key].split(",")
            for el in start_activities_strings:
                if el.strip() in executed_activities:
                    start_activities.add(el.strip())
    return start_activities


def get_end_activities(log, executed_activities, enabled_activities_key="enabled_activities"):
    end_activities = set()
    variants = pm4py.statistics.variants.log.get.get_variants(log)
    for variant in variants:
        trace = variants[variant][0]
        if len(trace) > 0:
            end_activities_strings = trace[-1][enabled_activities_key].split(",")
            for el in end_activities_strings:
                if el.strip() in executed_activities:
                    end_activities.add(el.strip())
    return end_activities


def get_directly_follow_relationships(log, executed_activities, enabled_activities_key="enabled_activities") -> dict:
    activity_follow = {}
    variants = pm4py.statistics.variants.log.get.get_variants(log)
    for variant in variants:
        trace = variants[variant][0]
        for index, current_event in enumerate(trace):
            if index < len(trace)-1:
                executed_activity = current_event["concept:name"]
                enabled_activities_next = [el.strip() for el in trace[index+1][enabled_activities_key].split(",") if el.strip() in executed_activities]
                if executed_activity not in activity_follow:
                    activity_follow[executed_activity] = set()
                for next_activity in enabled_activities_next:
                    activity_follow[executed_activity].add(next_activity)
    return activity_follow


def get_choice_relationships(log, executed_activities, enabled_activities_key="enabled_activities") -> dict:
    activity_choice = {}
    variants = pm4py.statistics.variants.log.get.get_variants(log)
    for variant in variants:
        trace = variants[variant][0]
        for index, current_event in enumerate(trace):
            if index < len(trace)-1:
                executed_activity = current_event["concept:name"]
                enabled_activities_current = set(
                    [el.strip() for el in current_event[enabled_activities_key].split(",") if
                     el.strip() in executed_activities])
                enabled_activities_next = set(
                    [el.strip() for el in trace[index + 1][enabled_activities_key].split(",") if
                     el.strip() in executed_activities])
                removed_activities = enabled_activities_current.difference(enabled_activities_next)
                for activity in removed_activities:
                    if executed_activity not in activity_choice:
                        activity_choice[executed_activity] = set()
                    activity_choice[executed_activity].add(activity)
                    if activity not in activity_choice:
                        activity_choice[activity] = set()
                    activity_choice[activity].add(executed_activity)
    return activity_choice


def get_parallel_relationships(log, executed_activities, enabled_activities_key="enabled_activities") -> dict:
    activity_parallel = {}
    variants = pm4py.statistics.variants.log.get.get_variants(log)
    for variant in variants:
        trace = variants[variant][0]
        for index, current_event in enumerate(trace):
            if index < len(trace)-1:
                executed_activity = current_event["concept:name"]
                enabled_activities_current = set([el.strip() for el in current_event[enabled_activities_key].split(",") if el.strip() in executed_activities])
                enabled_activities_next = set([el.strip() for el in trace[index+1][enabled_activities_key].split(",") if el.strip() in executed_activities])
                still_enabled = enabled_activities_current.intersection(enabled_activities_next)
                for activity in still_enabled:
                    if executed_activity not in activity_parallel:
                        activity_parallel[executed_activity] = set()
                    activity_parallel[executed_activity].add(activity)
                    if activity not in activity_parallel:
                        activity_parallel[activity] = set()
                    activity_parallel[activity].add(executed_activity)
    return activity_parallel


def get_parallel_relationships_frequent(log, executed_activities, enabled_activities_key="enabled_activities") -> dict:
    activity_parallel = {}
    variants = pm4py.statistics.variants.log.get.get_variants(log)
    for variant in variants:
        trace = variants[variant][0]
        number_of_occurrence = len(variants[variant])
        for index, current_event in enumerate(trace):
            if index < len(trace)-1:
                executed_activity = current_event["concept:name"]
                enabled_activities_current = set([el.strip() for el in current_event[enabled_activities_key].split(",") if el.strip() in executed_activities])
                enabled_activities_next = set([el.strip() for el in trace[index+1][enabled_activities_key].split(",") if el.strip() in executed_activities])
                still_enabled = enabled_activities_current.intersection(enabled_activities_next)
                for activity in still_enabled:
                    if (executed_activity, activity) not in activity_parallel:
                        activity_parallel[(executed_activity, activity)] = 0
                    activity_parallel[(executed_activity, activity)] += number_of_occurrence
                    if (activity, executed_activity) not in activity_parallel:
                        activity_parallel[(activity, executed_activity)] = 0
                    activity_parallel[(activity, executed_activity)] += number_of_occurrence
    return activity_parallel


def get_start_activities_frequent(log, executed_activities, enabled_activities_key="enabled_activities"):
    start_activities = {}
    variants = pm4py.statistics.variants.log.get.get_variants(log)
    for variant in variants:
        number_of_occurrence = len(variants[variant])
        trace = variants[variant][0]
        if len(trace) > 0:
            start_activities_strings = trace[0][enabled_activities_key].split(",")
            for el in start_activities_strings:
                if el.strip() in executed_activities:
                    if not el.strip() in start_activities:
                        start_activities[el.strip()] = 0
                    start_activities[el.strip()] += number_of_occurrence
    return start_activities


def get_end_activities_frequent(log, executed_activities, enabled_activities_key="enabled_activities"):
    end_activities = {}
    variants = pm4py.statistics.variants.log.get.get_variants(log)
    for variant in variants:
        number_of_occurrence = len(variants[variant])
        trace = variants[variant][0]
        if len(trace) > 0:
            end_activities_strings = trace[-1][enabled_activities_key].split(",")
            for el in end_activities_strings:
                if el.strip() in executed_activities:
                    if not el.strip() in end_activities:
                        end_activities[el.strip()] = 0
                    end_activities[el.strip()] += number_of_occurrence
    return end_activities


def get_choice_relationships_frequent(log, executed_activities, enabled_activities_key="enabled_activities") -> dict:
    activity_choice = {}
    variants = pm4py.statistics.variants.log.get.get_variants(log)
    for variant in variants:
        number_of_occurrence = len(variants[variant])
        trace = variants[variant][0]
        for index, current_event in enumerate(trace):
            if index < len(trace)-1:
                executed_activity = current_event["concept:name"]
                enabled_activities_current = set(
                    [el.strip() for el in current_event[enabled_activities_key].split(",") if
                     el.strip() in executed_activities])
                enabled_activities_next = set(
                    [el.strip() for el in trace[index + 1][enabled_activities_key].split(",") if
                     el.strip() in executed_activities])
                removed_activities = enabled_activities_current.difference(enabled_activities_next)
                for activity in removed_activities:
                    if (executed_activity, activity) not in activity_choice:
                        activity_choice[(executed_activity, activity)] = 0
                    activity_choice[(executed_activity, activity)] += number_of_occurrence
                    if (activity, executed_activity) not in activity_choice:
                        activity_choice[(activity, executed_activity)] = 0
                    activity_choice[(activity, executed_activity)] += number_of_occurrence
    return activity_choice


def get_directly_follow_relationships_frequent(log, executed_activities, enabled_activities_key="enabled_activities") -> dict:
    activity_follow = {}
    variants = pm4py.statistics.variants.log.get.get_variants(log)
    for variant in variants:
        number_of_occurrence = len(variants[variant])
        trace = variants[variant][0]
        for index, current_event in enumerate(trace):
            if index < len(trace)-1:
                executed_activity = current_event["concept:name"]
                enabled_activities_next = [el.strip() for el in trace[index+1][enabled_activities_key].split(",") if el.strip() in executed_activities]
                for next_activity in enabled_activities_next:
                    if not (executed_activity, next_activity) in activity_follow:
                        activity_follow[(executed_activity, next_activity)] = 0
                    activity_follow[(executed_activity, next_activity)] += number_of_occurrence
    return activity_follow
