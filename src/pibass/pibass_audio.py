#!/usr/bin/env python

import aubio
import argparse
import boto3
import io
import pydub
import pydub.playback
import threading

from pibass_motors import *


def text_to_mp3_stream(
    text='This is a test.',
    aws_region='us-east-1',
    polly_voice_id='Kimberly',
    mp3_sample_rate=22050):
  polly = boto3.client('polly', aws_region)
  response = polly.synthesize_speech(
    Text=text,
    OutputFormat='mp3',
    SampleRate=str(mp3_sample_rate),
    TextType='text',
    VoiceId=polly_voice_id)
  # For more voices, see: http://boto3.readthedocs.io/en/latest/reference/services/polly.html#Polly.Client.synthesize_speech
  # or http://docs.aws.amazon.com/polly/latest/dg/API_Voice.html

  stream = response["AudioStream"]
  mp3_bytes = stream.read()
  stream.close()
  return mp3_bytes


def save_mp3_stream(mp3_bytes, output_file):
  with(open(output_file, 'wb')) as f:
    f.write(mp3_bytes)


def play_mp3_stream(mp3_bytes):
  sound = pydub.AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
  pydub.playback.play(sound)


class PiBassAudio(PiBassAsyncMotors):
  def __init__(self, audio_temp_filepath='/tmp/pibass_audio.mp3',
      audio_sample_rate=22050,
      onset_buf_size=512, onset_hop_size=256, onset_method='mkl'):
    super(PiBassAudio, self).__init__()
    self.audio_temp_filepath = audio_temp_filepath
    self.audio_sample_rate = audio_sample_rate
    self.audio_mutex = threading.Lock()
    self.onset_buf_size = onset_buf_size
    self.onset_hop_size = onset_hop_size
    self.onset_method = onset_method

    self.onset_detector = aubio.onset(self.onset_method,
      self.onset_buf_size, self.onset_hop_size, self.audio_sample_rate)


  def generate_onset_motor_events(self, audio_path, mouth_open_sec_min=0.05, mouth_open_sec_max=0.1, mouth_move_sec=0.12):
    # Load audio stream
    audio_stream = aubio.source(audio_path, self.audio_sample_rate, self.onset_hop_size)

    # Detect all onsets
    onsets = []
    read = self.onset_hop_size # default
    total_frames = 0
    while read < self.onset_hop_size:
      samples, read = audio_stream()
      total_frames += read
      if self.onset_detector(samples):
        onsets.append(self.onset_detector.get_last_s())

    print('All onsets:\n%s\n' % '\n- '.join('%d' % o for o in onsets))

    # Insert motor events
    min_event_gap_sec = 2*mouth_move_sec+mouth_open_sec_min
    audio_total_s = total_frames*audio_stream.samplerate
    onsets.append(audio_total_s) # Insert end-of-file time
    prev_t = None
    now = time.time()
    for onset_t in onsets:
      t = now + onset_t
      if prev_t is not None:
        dt_max = t - prev_t
        if dt_max < min_event_gap_sec: # skip
          continue
        mouth_open_sec = random.uniform(mouth_open_sec_min, mouth_open_sec_max)
        self.move_mouth(delay_move=mouth_move_sec,
                        delay_open=mouth_open_sec,
                        t=t)
        print('move_mouth(%.1f, %.1f, %.1f)' % (mouth_move_sec, mouth_open_sec, t))
      prev_t = t


  def speak(self, text):
    with self.audio_mutex:
      #mp3_stream = text_to_mp3_stream(text=text, mp3_sample_rate=self.audio_sample_rate)
      #save_mp3_stream(mp3_stream, self.audio_temp_filepath)
      self.generate_onset_motor_events(self.audio_temp_filepath)
      #play_mp3_stream(mp3_stream)


def test_pibass_audio():
  parser = argparse.ArgumentParser()
  parser.add_argument('text', help='Text to be spoken', type=str)
  #parser.add_argument('--aws_region', help='AWS Region [us-east-1]', type=str, default='us-east-1')
  #parser.add_argument('--polly_voice_id', help='AWS Polly Voice ID [Kimberly]', type=str, default='Kimberly')
  #parser.add_argument('--mp3_sample_rate', help='MP3 Sample Rate [22050]', type=int, default=22050)
  args = parser.parse_args()
  
  bass = PiBassAudio()
  bass.speak(args.text)
  time.sleep(0.5)
  bass.terminate()


def test_polly_text_to_speech():
  parser = argparse.ArgumentParser()
  parser.add_argument('text', help='Text to be spoken', type=str)
  parser.add_argument('--aws_region', help='AWS Region [us-east-1]', type=str, default='us-east-1')
  parser.add_argument('--polly_voice_id', help='AWS Polly Voice ID [Kimberly]', type=str, default='Kimberly')
  parser.add_argument('--mp3_sample_rate', help='MP3 Sample Rate [22050]', type=int, default=22050)
  args = parser.parse_args()

  mp3_stream = text_to_mp3_stream(text=args.text, aws_region=args.aws_region, polly_voice_id=args.polly_voice_id, mp3_sample_rate=args.mp3_sample_rate)
  play_mp3_stream(mp3_stream)
  save_mp3_stream(mp3_stream, 'polly_output.mp3')


if __name__ == '__main__':
  #test_polly_text_to_speech()
  test_pibass_audio()
