import argparse

from googletrans import Translator


def detect_language(text):
    translator = Translator()
    result = translator.detect(text)

    print('Text: {}'.format(text))
    print('Confidence: {}'.format(result.confidence))
    print('Language: {}'.format(result.lang))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('text')
    args = parser.parse_args()
    detect_language(args.text)
