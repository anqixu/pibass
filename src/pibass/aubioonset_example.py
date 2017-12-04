#!/usr/bin/env python

import sys
from aubio import source, onset

win_s = 512                 # fft size
hop_s = win_s // 2          # hop size

if len(sys.argv) < 2:
    print("Usage: %s <filename> [method]" % sys.argv[0])
    sys.exit(1)

filename = sys.argv[1]
samplerate = 0
method = "default"
if len( sys.argv ) > 2: method = sys.argv[2]

s = source(filename, samplerate, hop_s)
samplerate = s.samplerate

o = onset(method, win_s, hop_s, samplerate)

# list of onsets, in samples
onsets = []

# total number of frames read
total_frames = 0
while True:
    samples, read = s()
    if o(samples):
        print("%f" % o.get_last_s())
        onsets.append(o.get_last())
    total_frames += read
    if read < hop_s: break
#print len(onsets)

"""
./aubioonset_example.py this_is_a_test.mp3 default

  [Thi]s: 0.13-0.25
  Thi[s]: 0.25-0.38
  [i]s:   0.42-0.49
  i[s]:   0.49-0.64
  [a]:    0.64-0.7
  [te]st: 0.7-0.9
  te[st]: 0.9-1.1

  mkl [frequent] [BEST]
0.260635 Thi[s]
0.428209 [i]s + i[s]
0.641995 [a]
0.718141 [te]st
0.912880 te[st]
0.963991 ...

  specflux [too frequent]
0.051383 lead-up to This
0.118186 [Thi]s
0.248889 Thi[s]
0.420136 [i]s
0.540453 i[s]
0.632789 [a]
0.708435 [te]st
0.900635 te[st]
1.051882 ...

  kl [premature]
0.014104 lead-up to This / [Thi]s
0.259365 Thi[s]
0.428254 [i]s + i[s]
0.639456 [a]
0.718277 [te]st
0.915918 te[st]

  specdiff [premature+frequent]
0.056916 lead-up to This
0.126848 [Thi]s
0.271156 Thi[s]
0.440091 [i]s
0.549116 i[s]
0.645896 [a]
0.728753 [te]st
0.914104 te[st]

  wphase [premature+frequent]
0.056689 lead-up to This
0.125351 [Thi]s
0.182630 part of [Thi]s
0.270930 Thi[s]
0.434739 [i]s
0.548889 i[s]
0.640408 [a]
0.720499 [te]st
0.912426 te[st]

  default: [frequent/missing]
0.132245 [Thi]s
0.270476 Thi[s]
0.442540 [i]s + i[s]
0.639547 [a]
MISSING  [te]st
0.913424 te[st]
0.966032 ...

  energy: [premature+too frequent]
0.059002 empty
0.129977 [Thi]s
0.291519 Thi[s]
0.440363 [i]s
0.550975 mid of i[s]
0.643084 [a]
0.720000 [te]st
0.938957 te[st]

  hfc: [frequent/missing]
0.132245 [Thi]s
0.270476 Thi[s]
0.442540 [i]s + i[s]
0.639547 [a]
MISSING  [te]st
0.913424 te[st]
0.966032 ...

  complex [too missing]
MISSING  [Thi]s + Thi[s]
0.428163 [i]s + i[s]
0.642313 [a]
MISSING  [te]st
0.912336 te[st]

  phase [premature/missing]
0.056961 lead-up to This
0.128435 [Thi]s
0.432290 [i]s
0.640771 [a]
MISSING  [te]st
0.903084 te[st]
"""
