import numpy as np


def parse_stacktrace_report_to_json(report):
    cluster_desc = []
    cluster_reports = []
    for cluster_id, eval_report in report.cluster_report.evaluation_report.items():
        cluster_dict = {
            'cluster_id': cluster_id,
            'match_exactly': eval_report.match_exactly,
            'num_error_logs': eval_report.num_error_logs,
            'num_unique_stacktrace': eval_report.num_unique_stacktrace,
            'percent_unique_stacktrace': eval_report.percent_unique_stacktrace,
            'representation': eval_report.representation,
            'error_log_ids': eval_report.error_log_ids,
            'docids': eval_report.docids
        }
        cluster_reports.append(cluster_dict)
        cluster_desc.append(eval_report.num_error_logs)
    sorted_cluster_idx = np.argsort(cluster_desc)[::-1]
    cluster_reports = [cluster_reports[i] for i in sorted_cluster_idx]
    report = {'cluster_report': cluster_reports,
              'data_report': {'valid': report.data_report.valid_data,
                              'excluded': report.data_report.exclude_indices}}
    return report
