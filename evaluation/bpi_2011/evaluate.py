from synthetical_log_generation.log_generator import create_translucent_event_log
from synthetical_log_generation.log_generator import create_logs
from translucent_discovery.translucent_inductive_miner.translucent_base import discover_petri_net
import pm4py
from pm4py.objects.conversion.log import converter as log_converter
from translucent_precision.main import translucent_precision_score
from evaluation.translucent_f_1_score import compute_f_1_scores
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

initial_log = pm4py.read_xes("Hospital_log.xes")
initial_log = log_converter.apply(initial_log, variant=log_converter.Variants.TO_EVENT_LOG)


def evaluate(log, threshold):
    if threshold == 0.8:
        base = "08"
    elif threshold == 0.6:
        base = "06"
    elif threshold == 0.4:
        base = "04"
    elif threshold == 0.2:
        base = "02"
    else:
        base = "None"

    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log, noise_threshold=threshold)
    # add translucent information
    log = create_translucent_event_log(log, net, initial_marking, final_marking)
    dataframe = pm4py.convert_to_dataframe(log)
    dataframe.to_csv(base + '/ground_truth.csv', sep=",", index=False)
    # create sublogs
    dataframe_list = create_logs(log)
    i = 0
    while i < len(dataframe_list):
        dataframe_list[i].to_csv(base+"/"+str(i + 1) + '.csv', sep=",", index=False)
        i += 1
    im_fitness = []
    im_precision = []

    imto_fitness = []
    imto_precision = []

    imtf_fitness = []
    imtf_precision = []

    imts_fitness = []
    imts_precision = []
    i = 0
    while i < len(dataframe_list):
        sub_log = log_converter.apply(dataframe_list[i], variant=log_converter.Variants.TO_EVENT_LOG)
        i += 1
        print(i)
        model, i_m, f_m = discover_petri_net(sub_log, {"translucent_variant": "IM"})
        im_fitness.append(pm4py.conformance.fitness_alignments(log, model, i_m, f_m)["log_fitness"])
        im_precision.append(translucent_precision_score(log, model, i_m, f_m))

        model, i_m, f_m = discover_petri_net(sub_log, {"translucent_variant": "IMto"})
        imto_fitness.append(pm4py.conformance.fitness_alignments(log, model, i_m, f_m)["log_fitness"])
        imto_precision.append(translucent_precision_score(log, model, i_m, f_m))

        model, i_m, f_m = discover_petri_net(sub_log, {"translucent_variant": "IMtf"})
        imtf_fitness.append(pm4py.conformance.fitness_alignments(log, model, i_m, f_m)["log_fitness"])
        imtf_precision.append(translucent_precision_score(log, model, i_m, f_m))

        model, i_m, f_m = discover_petri_net(sub_log, {"translucent_variant": "IMts"})
        imts_fitness.append(pm4py.conformance.fitness_alignments(log, model, i_m, f_m)["log_fitness"])
        imts_precision.append(translucent_precision_score(log, model, i_m, f_m))

    im_f1 = compute_f_1_scores(im_fitness, im_precision)
    imto_f1 = compute_f_1_scores(imto_fitness, imto_precision)
    imtf_f1 = compute_f_1_scores(imtf_fitness, imtf_precision)
    imts_f1 = compute_f_1_scores(imts_fitness, imts_precision)

    result_im = pd.DataFrame({"Fitness": im_fitness, "Precision": im_precision, "F1_Score": im_f1})
    result_im.to_csv(base + "/im_result.csv", sep=",", index=False)

    result_imto = pd.DataFrame({"Fitness": imto_fitness, "Precision": imto_precision, "F1_Score": imto_f1})
    result_imto.to_csv(base + "/imto_result.csv", sep=",", index=False)

    result_imtf = pd.DataFrame({"Fitness": imtf_fitness, "Precision": imtf_precision, "F1_Score": imtf_f1})
    result_imtf.to_csv(base + "/imtf_result.csv", sep=",", index=False)

    result_imts = pd.DataFrame({"Fitness": imts_fitness, "Precision": imts_precision, "F1_Score": imts_f1})
    result_imts.to_csv(base + "/imts_result.csv", sep=",", index=False)

    algorithms = ['IM', 'IMto', 'IMtf', 'IMts']
    criteria = ['Fitness', 'Precision', 'F1-Score']
    algorithm_colors = ['blue', 'green', 'red', 'purple']
    data = {
        'IM': {
            'Fitness': im_fitness,
            'Precision': im_precision,
            'F1-Score': im_f1
        },
        'IMto': {
            'Fitness': imto_fitness,
            'Precision': imto_precision,
            'F1-Score': imto_f1
        },
        'IMtf': {
            'Fitness': imtf_fitness,
            'Precision': imtf_precision,
            'F1-Score': imtf_f1
        },
        'IMts': {
            'Fitness': imts_fitness,
            'Precision': imts_precision,
            'F1-Score': imts_f1
        }
    }

    # Create subplots
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    # Plot data for each criterion
    for i, criterion in enumerate(criteria):
        ax = axs[i]
        ax.set_title(criterion, fontsize=14)
        ax.set_xlabel('Number of Variants', fontsize=12)
        ax.set_xticks(np.insert(np.arange(4, len(data["IM"]["Fitness"]), 5), 0, 0))
        ax.set_xticklabels([str(i) for i in np.insert(np.arange(5, len(data["IM"]["Fitness"]) + 1, 5), 0, 1)])
        ax.tick_params(axis='x', which='major', labelsize=10, size=5)
        for algo, color in zip(algorithms, algorithm_colors):
            ax.plot(data[algo][criterion], label=algo, marker='o', color=color)
    # Add legend below subplots
    fig.legend(algorithms, loc='lower center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True,
               ncol=len(algorithms))

    # Adjust layout
    plt.tight_layout()

    # Save plot as a tight PDF
    plt.savefig(base + "/result_5.pdf", bbox_inches="tight")

    # Create subplots
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    # Plot data for each criterion
    for i, criterion in enumerate(criteria):
        ax = axs[i]
        ax.set_title(criterion, fontsize=14)
        ax.set_xlabel('Number of Variants', fontsize=12)
        ax.set_xticks(np.insert(np.arange(4, len(data["IM"]["Fitness"]), 10), 0, 0))
        ax.set_xticklabels([str(i) for i in np.insert(np.arange(5, len(data["IM"]["Fitness"]) + 1, 10), 0, 1)])
        ax.tick_params(axis='x', which='major', labelsize=10, size=5)
        for algo, color in zip(algorithms, algorithm_colors):
            ax.plot(data[algo][criterion], label=algo, marker='o', color=color)
    # Add legend below subplots
    fig.legend(algorithms, loc='lower center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True,
               ncol=len(algorithms))

    # Adjust layout
    plt.tight_layout()

    # Save plot as a tight PDF
    plt.savefig(base + "/result_10.pdf", bbox_inches="tight")


settings = [0.8, 0.6, 0.4, 0.2]
for s in settings:
    evaluate(initial_log, s)
