from ..DataProcessing import ExtractFeatures


def segment_data(array, segment_size, window_size):

    segmented_data = []
    size = len(array)

    for i in range(0, size, window_size):
        window = array[i: (i + segment_size)]
        actual_window_size = len(window)
        if actual_window_size < segment_size:
            break

        result = ExtractFeatures.extract_features(window)
        segmented_data.append(result)

    return segmented_data
