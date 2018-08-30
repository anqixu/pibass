#!/usr/bin/env python

# Inventory of Amazon polly voices
# From: https://us-west-2.console.aws.amazon.com/polly/home/SynthesizeSpeech
voice_db = [
    ('Naja', 'female', 'dv'),
    ('Mads', 'male', 'dv'),
    ('Lotte', 'female', 'nl'),
    ('Ruben', 'male', 'nl'),
    ('Joanna', 'female', 'en-us'),
    ('Salli', 'female', 'en-us'),
    ('Kimberly', 'female', 'en-us'),
    ('Kendra', 'female', 'en-us'),
    ('Ivy', 'female', 'en-us'),
    ('Matthew', 'male', 'en-us'),
    ('Justin', 'male', 'en-us'),
    ('Joey', 'male', 'en-us'),
    ('Nicole', 'female', 'en-au'),
    ('Russell', 'male', 'en-au'),
    ('Emma', 'female', 'en-gb'),
    ('Amy', 'female', 'en-gb'),
    ('Brian', 'male', 'en-gb'),
    ('Aditi', 'female', 'en-in'),
    ('Raveena', 'female', 'en-in'),
    ('Geraint', 'male', 'cy'),
    ('Chantal', 'female', 'fr-ca'),
    ('Celine', 'female', 'fr'),
    ('Mathieu', 'male', 'fr'),
    ('Vicki', 'female', 'de'),
    ('Marlene', 'female', 'de'),
    ('Hans', 'male', 'de'),
    ('Dora', 'female', 'is'),
    ('Karl', 'male', 'is'),
    ('Carla', 'female', 'it'),
    ('Giorgio', 'male', 'it'),
    ('Mizuki', 'female', 'ja'),
    ('Takumi', 'male', 'ja'),
    ('Seoyeon', 'female', 'ko'),
    ('Liv', 'female', 'no'),
    ('Ewa', 'female', 'pl'),
    ('Maja', 'female', 'pl'),
    ('Jan', 'male', 'pl'),
    ('Jacek', 'male', 'pl'),
    ('Ines', 'female', 'pt'),
    ('Cristiano', 'male', 'pt'),
    ('Vitoria', 'female', 'pt-br'),
    ('Ricardo', 'male', 'pt-br'),
    ('Carmen', 'female', 'ro'),
    ('Tatyana', 'female', 'ru'),
    ('Maxim', 'male', 'ru'),
    ('Conchita', 'female', 'es'),
    ('Enrique', 'male', 'es'),
    ('Penelope', 'female', 'es-us'),
    ('Miguel', 'male', 'es-us'),
    ('Astrid', 'female', 'sv'),
    ('Filiz', 'female', 'tr'),
    ('Gwyneth', 'female', 'cy')]


"""
Returns tuple: (polly_name, gender, language_code)

query can be either:
- language code
- language code, female/male
- Polly voice name
"""


def get_voice(query):
    try:
        # Assume language code, gender
        if query.find(',') >= 0:
            query_lang, query_gender = query.split(',')
            query_lang = query_lang.strip()
            query_gender = query_gender.strip().lower()

            for v, g, l in voice_db:
                if g == query_gender and (l.find(query_lang) == 0):
                    return v, g, l

        else:  # Assume language code
            query_lang = query.strip()
            for v, g, l in voice_db:
                if l.find(query_lang) == 0:
                    return v, g, l

        # Assume voice name
        query_voice = query.strip().lower()
        for v, g, l in voice_db:
            if v.lower() == query_voice:
                return v, g, l

    except ValueError:
        pass

    return None, None, None


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Test get_voice')
    parser.add_argument(
        'query', help='either language code, or (language code, female/male), or Polly voice name')
    args = parser.parse_args()
    print(get_voice(args.query))
