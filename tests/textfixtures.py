import os.path
from core.extract import format_filename
from tests.settings import TEST_TEXT_DIR


TEXTS_DISTRIBUTIONS = {
    'R': [
        {'a': 0.20, 'b': 0.28, 'c': 0.43,  'd': 0.07, 'e': 0.02, 'f':0.00},
        {'a': 0.15, 'b': 0.13, 'c': 0.39,  'd': 0.33, 'e': 0.00, 'f':0.00},
        {'a': 0.17, 'b': 0.21, 'c': 0.46,  'd': 0.16, 'e': 0.00, 'f':0.00},
        {'a': 0.25, 'b': 0.21, 'c': 0.52,  'd': 0.02, 'e': 0.00, 'f':0.00},
        {'a': 0.29, 'b': 0.28, 'c': 0.32,  'd': 0.08, 'e': 0.03, 'f':0.00},
        {'a': 0.12, 'b': 0.25, 'c': 0.56,  'd': 0.07, 'e': 0.00, 'f':0.00},
        {'a': 0.13, 'b': 0.30, 'c': 0.36,  'd': 0.21, 'e': 0.00, 'f':0.00},
        {'a': 0.24, 'b': 0.30, 'c': 0.37,  'd': 0.09, 'e': 0.00, 'f':0.00},
        {'a': 0.21, 'b': 0.28, 'c': 0.32,  'd': 0.19, 'e': 0.00, 'f':0.00},
        {'a': 0.14, 'b': 0.10, 'c': 0.59,  'd': 0.17, 'e': 0.00, 'f':0.00}
    ],
    'E': [
        {'a': 0.13, 'b': 0.12, 'c': 0.18,  'd': 0.57, 'e': 0.00, 'f':0.00},
        {'a': 0.28, 'b': 0.15, 'c': 0.00,  'd': 0.57, 'e': 0.00, 'f':0.00},
        {'a': 0.24, 'b': 0.13, 'c': 0.01,  'd': 0.62, 'e': 0.00, 'f':0.00},
        {'a': 0.24, 'b': 0.15, 'c': 0.15,  'd': 0.45, 'e': 0.00, 'f':0.01},
        {'a': 0.29, 'b': 0.15, 'c': 0.13,  'd': 0.43, 'e': 0.00, 'f':0.00},
        {'a': 0.20, 'b': 0.16, 'c': 0.09,  'd': 0.55, 'e': 0.00, 'f':0.00},
        {'a': 0.17, 'b': 0.27, 'c': 0.06,  'd': 0.50, 'e': 0.00, 'f':0.00},
        {'a': 0.29, 'b': 0.24, 'c': 0.11,  'd': 0.36, 'e': 0.00, 'f':0.00},
        {'a': 0.12, 'b': 0.30, 'c': 0.10,  'd': 0.48, 'e': 0.00, 'f':0.00},
        {'a': 0.17, 'b': 0.21, 'c': 0.16,  'd': 0.46, 'e': 0.00, 'f':0.00}
    ]
}


def distributions():
    for period, texts in TEXTS_DISTRIBUTIONS.items():
        for i, distribution in enumerate(texts):
            title = "%s%d" % (period, i + 1)
            filename  = format_filename(author="test", title=title)
            yield filename, distribution


def bootstrap():
    for filename, distribution in distributions():
        try:
            os.mkdirs(TEST_TEXT_DIR)
        except:
            pass
        path = os.path.join(TEST_TEXT_DIR, filename)
        f = open(path, "w")
        for letter, frequency in distribution.items():
            s = " ".join([letter] * int(frequency * 100))
            f.write(s)
            f.write("\n")
        f.close()
