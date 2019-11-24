import re


def find_stacktrace_representation(list_stacktrace):
    assert isinstance(list_stacktrace, list)
    assert len(list_stacktrace) > 0
    min_length = min(len(stacktrace) for stacktrace in list_stacktrace)
    representation = []
    for i in range(min_length):
        validation = True
        method = list_stacktrace[0][i]
        diff = []
        for j in range(1, len(list_stacktrace)):
            if list_stacktrace[j][i] != method:
                validation = False
                diff += [list_stacktrace[j][i]]
        if validation:
            representation += [method]
        else:
            method_rep = diff[0]
            for diff_method in set(diff):
                method_rep = extract_longest_common_sequences(method_rep, diff_method)
            representation += ['===>' + method_rep + '<===']
    return representation


def extract_longest_common_sequences(text1, text2, representation="[...]"):
    # TODO: Enhance extract_longest_common_sequences for multiple comparing
    alter_text = ''
    i = 0
    j = 0
    while i < len(text1) and j < len(text2):
        i_t = i
        j_t = j
        if text1[i] == text2[j]:
            while i_t < len(text1) and j_t < len(text2) and text1[i_t] == text2[j_t]:
                alter_text += text1[i_t]
                i_t += 1
                j_t += 1
            # Update lastest positions
            i = i_t
            j = j_t
        else:
            positions = []
            lengths = []
            while i_t < len(text1):
                # Scan longest character sequence
                while j_t < len(text2) - 1:
                    if text1[i_t] == text2[j_t]:
                        i_t1 = i_t
                        j_t1 = j_t
                        while i_t1 < len(text1) and j_t1 < len(text2) and text1[i_t1] == text2[j_t1]:
                            i_t1 += 1
                            j_t1 += 1
                        # Reserve position and length
                        positions.append((i_t, j_t))
                        lengths.append(j_t1 - j_t)
                    j_t += 1
                # Scan the next position of t1
                i_t += 1
                # Re position at the beginning of j
                j_t = j
            # Update lastest positions
            if len(lengths) > 0:
                i, j = positions[lengths.index(max(lengths))]
                alter_text += representation
            else:
                i, j = i_t, j_t
                alter_text += representation
    return alter_text


def parse_with_regex(logs):
    return [re.findall("(?<=\tat ).+(?=[(].+[)][\r\n])", l) for l in logs]
