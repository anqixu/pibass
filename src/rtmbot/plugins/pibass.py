from __future__ import print_function
from __future__ import unicode_literals

from rtmbot.core import Plugin
import re
import googletrans

from pibass import get_voice, PiBassAudio


# Remove tags and clean up string
def filter_text(msg):
  msg = re.sub('<@[a-zA-Z0-9]*>', '', msg)
  msg = re.sub('<#[a-zA-Z0-9]*>', '', msg)
  msg = re.sub('\s\s+', ' ', msg)
  msg = msg.strip()
  return msg


class TTSPlugin(Plugin):
  def __init__(self, *kargs, **kwargs):
    super().__init__(*kargs, **kwargs)
    self.trans = googletrans.Translator()
    self.bass = PiBassAudio(args, audio_sample_rate=22050)
bass.speak(args.text)

  """
  Returns language_code, confidence

  Implementation uses unofficial Google Translate API.
  """
  def detect_language(self, text):
    result = self.trans.detect(text)
    return result.lang, result.confidence

  def process_message(self, data):
    if 'text' in data:
      # Extract message
      msg = filter_text(data['text'])

      # Identify voice
      match = re.search("^\[.*\]", msg)
      if match is not None: # Scan for manual language/gender/voice
        query = msg[1:match.end()-1]
        msg = msg[match.end():].strip()
        voice, gender, lang_code = get_voice(query)
      else: # Detect language
        lang, lang_conf = self.detect_language(msg)
        lang = lang.lower()
        voice, gender, lang_code = get_voice(lang)
        if voice is None and len(lang) > 2:
          lang = lang[:2]
          voice, gender, lang_code = get_voice(lang)
      if voice is None: # Default to English
        voice, gender, lang_code = get_voice('en')
      
      # Synthesize voice
      print(msg, voice, lang_code)
    #  self.outputs.append([data['channel'], 'from repeat1 "{}" in channel {}'.format(data['text'], data['channel'])])
