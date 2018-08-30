#!/usr/bin/env python

import argparse
import pyaudio
import pydub
import io
import random
import time
import threading

try:
    from .audio_utils import OnsetDetector, text_to_mp3_stream, save_mp3_stream
    from .pibass_motors import PiBassAsyncMotors
except (ImportError, ValueError) as err:
    from audio_utils import OnsetDetector, text_to_mp3_stream, save_mp3_stream
    from pibass_motors import PiBassAsyncMotors


class PiBassAudio(PiBassAsyncMotors):
    def __init__(self, args=None, audio_temp_filepath='/tmp/pibass_audio.mp3'):
        super(PiBassAudio, self).__init__()
        self.args = args
        self.audio_sample_rate = args.mp3_sample_rate if args else 22050
        self.audio_temp_filepath = audio_temp_filepath
        self.audio_mutex = threading.Lock()
        self.onset_detector = OnsetDetector(
            audio_sample_rate=self.audio_sample_rate)
        self.audio_dev = pyaudio.PyAudio()

    def terminate(self):
        super(PiBassAudio, self).terminate()
        self.audio_dev.terminate()

    def insert_onset_motor_events(self, onsets, mouth_open_sec_min=0.05, mouth_open_sec_max=0.1, mouth_move_sec=0.1, dt_offset=0.):
        # min_event_gap_sec = 2*mouth_move_sec+mouth_open_sec_min # disabled
        min_event_gap_sec = 0.1
        prev_t = time.time()
        mouth_start_t = prev_t
        for onset_t in onsets:
            t = mouth_start_t + dt_offset + onset_t
            dt_max = t - prev_t
            if dt_max < min_event_gap_sec:  # skip
                continue
            mouth_open_sec = random.uniform(
                mouth_open_sec_min, mouth_open_sec_max)
            self.move_mouth(delay_move=mouth_move_sec,
                            delay_open=mouth_open_sec,
                            release=False,
                            t=prev_t)
            # print('move_mouth(%.2f, %.2f, %.2f), o=%.2f po=%.2f dt=%.2f' % (mouth_move_sec, mouth_open_sec, prev_t, onset_t, prev_t-now, dt_max))
            prev_t = t

        # TODO: randomly insert tail motor events (mouth_start_t to prev_t)

    def speak(self, text, polly_voice_id=None, aws_region='us-east-1'):
        if self.args is not None:
            aws_region = self.args.aws_region or aws_region
            polly_voice_id = polly_voice_id or self.args.polly_voice_id

        with self.audio_mutex:
            # Notify initialization by moving head
            self.clear_all_events()
            t = self.move_head(open=True, release=False)

            # Obtain MP3 stream
            mp3_stream = text_to_mp3_stream(
                text=text, aws_region=aws_region,
                polly_voice_id=polly_voice_id,
                mp3_sample_rate=self.audio_sample_rate)

            # Compute onsets
            save_mp3_stream(mp3_stream, self.audio_temp_filepath)
            onsets = self.onset_detector.detect(self.audio_temp_filepath)

            # Load as pydub audio segment
            sound = pydub.AudioSegment.from_file(
                io.BytesIO(mp3_stream), format="mp3")

            # Start stream on physical audio device
            stream = self.audio_dev.open(
                format=self.audio_dev.get_format_from_width(
                    sound.sample_width),
                channels=sound.channels,
                rate=sound.frame_rate,
                output=True)

            # Insert onsets and immediately play audio
            self.insert_onset_motor_events(onsets)
            stream.write(sound._data)

            # Stop stream on physical audio device
            stream.stop_stream()
            stream.close()

            # Pause for a bit after playback
            time.sleep(0.5)


def test_pibass_audio():
    parser = argparse.ArgumentParser(description='Test pibass audio')
    parser.add_argument('text', help='Text to be spoken', type=str)
    parser.add_argument(
        '--aws_region', help='AWS Region [us-east-1]', type=str, default='us-east-1')
    parser.add_argument(
        '--polly_voice_id', help='AWS Polly Voice ID [Kimberly]', type=str, default='Kimberly')
    parser.add_argument('--mp3_sample_rate',
                        help='MP3 Sample Rate [22050]', type=int, default=22050)
    args = parser.parse_args()

    bass = PiBassAudio(args)
    bass.speak(args.text)
    bass.terminate()


if __name__ == '__main__':
    test_pibass_audio()
