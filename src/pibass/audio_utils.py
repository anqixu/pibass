#!/usr/bin/env python

import argparse
import aubio
import boto3
import io
import pyaudio
import pydub
import pydub.playback


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


def open_mp3_stream(mp3_file):
    with(open(mp3_file, 'rb')) as f:
        mp3_bytes = f.read()
    return mp3_bytes


def play_mp3_stream(mp3_bytes):
    sound = pydub.AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
    pydub.playback.play(sound)


def play_mp3_stream_pyaudio(mp3_bytes, cb_on_start=None):
    """Fine-grained play_mp3_stream that triggers callback right before playback.
    """
    sound = pydub.AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")

    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(sound.sample_width),
                    channels=sound.channels,
                    rate=sound.frame_rate,
                    output=True)

    if cb_on_start:
        cb_on_start()
    stream.write(sound._data)

    stream.stop_stream()
    stream.close()

    p.terminate()


class OnsetDetector:
    def __init__(self,
                 audio_sample_rate=22050,
                 onset_buf_size=512,
                 onset_hop_size=256,
                 onset_method='mkl'):
        self.audio_sample_rate = audio_sample_rate
        self.onset_buf_size = onset_buf_size
        self.onset_hop_size = onset_hop_size
        self.onset_method = onset_method

    def detect(self, audio_path):
        """ Returns list of floats corresponding to onsets. """

        # Load audio stream
        audio_stream = aubio.source(
            audio_path, self.audio_sample_rate, self.onset_hop_size)
        onset_detector = aubio.onset(self.onset_method,
                                     self.onset_buf_size,
                                     self.onset_hop_size,
                                     self.audio_sample_rate)

        # Detect all onsets
        onsets = []
        total_frames = 0
        read = self.onset_hop_size  # default value
        while read >= self.onset_hop_size:
            samples, read = audio_stream()
            total_frames += read
            if onset_detector(samples):
                onsets.append(onset_detector.get_last_s())
        audio_total_s = float(total_frames)/audio_stream.samplerate
        onsets.append(audio_total_s)  # Insert end-of-file time

        return onsets


def test_polly_text_to_speech():
    parser = argparse.ArgumentParser(
        description='Test AWS Polly test-to-speech')
    parser.add_argument('text', help='Text to be spoken', type=str)
    parser.add_argument(
        '--aws_region', help='AWS Region [us-east-1]', type=str, default='us-east-1')
    parser.add_argument(
        '--polly_voice_id', help='AWS Polly Voice ID [Kimberly]', type=str, default='Kimberly')
    parser.add_argument('--mp3_sample_rate',
                        help='MP3 Sample Rate [22050]', type=int, default=22050)
    args = parser.parse_args()

    mp3_stream = text_to_mp3_stream(text=args.text, aws_region=args.aws_region,
                                    polly_voice_id=args.polly_voice_id, mp3_sample_rate=args.mp3_sample_rate)
    play_mp3_stream(mp3_stream)
    save_mp3_stream(mp3_stream, 'polly_output.mp3')


def test_aubio_onset_detection(filename='this_is_a_test.mp3', method='mkl', win_s=512, hop_s=256, samplerate=0):
    s = aubio.source(filename, samplerate, hop_s)
    samplerate = s.samplerate
    print('Sample rate for %s: %d' % (filename, samplerate))
    o = aubio.onset(method, win_s, hop_s, samplerate)
    onsets = []
    while True:
        samples, read = s()
        if o(samples):
            print("%f" % o.get_last_s())
            onsets.append(o.get_last())
        if read < hop_s:
            break
    print(onsets)


if __name__ == '__main__':
    # test_aubio_onset_detection()
    test_polly_text_to_speech()
