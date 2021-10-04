import os
import moviepy.editor as mp
from moviepy.video.tools.subtitles import SubtitlesClip
from pydub import AudioSegment
from pydub.silence import split_on_silence
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import time
import datetime
from wit import Wit
import argparse
import sys


def add_audio_together(chunks_function, target_length_function):
    output_chunks_function = [chunks_function[0]]
    for chunk in chunks_function[1:]:
        if len(output_chunks_function[-1]) < target_length_function:
            output_chunks_function[-1] += chunk
        else:
            # if the last output chunk is longer than the target length,
            # we can start a new one
            output_chunks_function.append(chunk)
    return output_chunks_function


def convert_to_wav(src):
    video_function = mp.VideoFileClip(str(src))
    video_function.audio.write_audiofile("testtest.wav")
    return video_function


def read_wav_file_and_split(src):
    audio_file_function = AudioSegment.from_wav(src)

    dBFS = audio_file_function.dBFS
    # split file
    chunks_function = split_on_silence(
        audio_file_function,
        min_silence_len=250,
        silence_thresh=dBFS - 25,
        keep_silence=150,
    )

    return chunks_function, dBFS, audio_file_function


def save_chunks_temporarily(output_chunks_function):
    number_function = 0
    list_chunk_length_function = []
    for x_function, added_chunk in enumerate(output_chunks_function):
        added_chunk.export("test_test{0}.wav".format(x_function), format="wav")
        number_function = x_function

        list_chunk_length_function.append(round(added_chunk.duration_seconds, 2))
    return number_function, list_chunk_length_function


def create_video_chunks(video_function, number_function, added_chunk_list_function):
    video_length = video_function.duration
    clip_list_function = []
    for x_function in range(number_function):
        if x_function == 0:
            clip_list_function.append(video_function.subclip(0, added_chunk_list_function[x_function]))
        else:
            clip_list_function.append(video_function.subclip(added_chunk_list_function[x_function - 1],
                                                             added_chunk_list_function[x_function]))

    return clip_list_function


def transcribe_snippets(repetitions):
    access_token = ""

    if language == "englisch":
        access_token = "Access token"
    elif language == "deutsch":
        access_token = "Access token"
    else:
        sys.exit("wrong language")

    client = Wit(access_token=access_token)

    resp = None

    list_transcriptions_function = []

    for x_function in range(repetitions):
        try:
            with open('test_test' + str(x_function) + '.wav', 'rb') as f:
                resp = client.speech(f, {'Content-Type': 'audio/wav'})
                # print('response: ' + str(resp) + '; ')
                list_transcriptions_function.append(resp["text"])
        except:
            # print("error")
            list_transcriptions_function.append("error")

    return list_transcriptions_function


def generate_video(clip_list_function, transcriptions):
    list_text_clip = []
    new_video = None

    for x_function, video_clip in enumerate(clip_list_function):
        # only if length is greater then 65
        if len(transcriptions[x_function]) > 65:
            sub_subtitle = generate_text_chunks(transcriptions[x_function], 65)

            sub_parts_list = [0]

            chunk_sub_parts = video_clip.duration / sub_subtitle.__len__()

            for x_2 in range(sub_subtitle.__len__()): # todo überarbeiten
                if x_2 < len(sub_subtitle) - 1:
                    sub_parts_list.append((x_2 + 1) * chunk_sub_parts)

            sub_parts_list.append(video_clip.duration)

            for y, sub_subtitles in enumerate(sub_subtitle):
                text_name = str(sub_subtitles)
                txt_clip = mp.TextClip(text_name, fontsize=25, color="red")
                txt_clip = txt_clip.set_position('bottom')

                txt_clip = txt_clip.set_duration(chunk_sub_parts)

                sub_clip = video_clip.subclip(sub_parts_list[y], sub_parts_list[y + 1])

                list_text_clip.append(mp.CompositeVideoClip([sub_clip, txt_clip]))

        else:
            text_name = str(transcriptions[x_function])
            txt_clip = mp.TextClip(text_name, fontsize=25, color="red")
            txt_clip = txt_clip.set_position('bottom')

            if x_function == clip_list_function.__len__() - 1:
                txt_clip = txt_clip.set_duration(list_chunk_length[x_function])
                list_text_clip.append(mp.CompositeVideoClip([video_clip, txt_clip]))
            else:
                txt_clip = txt_clip.set_duration(list_chunk_length[x_function])
                list_text_clip.append(mp.CompositeVideoClip([video_clip, txt_clip]))

    new_video.write_videofile(file_name+"_Untertitel.mp4")


def fix_length_audio(chunks_, dBFS, audio_file_function, test_function):
    new_list = []
    target_length_function = 10 * 1000
    for chunk in chunks_:
        if chunk.duration_seconds > 20:
            # split audio
            # split file
            chunks_function = split_on_silence(
                chunk,
                min_silence_len=50,
                silence_thresh=dBFS - 23,
                keep_silence=150,
            )
            new_list.extend(add_audio_together(chunks_function, target_length_function))
        else:
            new_list.append(chunk)
    # create last snippet
    t_finish = audio_file_function.duration_seconds
    t_start = (t_finish - test_function) * 1000
    splitted_audio = audio_file_function[-t_start:]
    new_list.append(splitted_audio)
    return new_list


def generate_text_chunks(text, length):
    splitted = text.split(" ")

    text_list = []
    text = ""
    for splits in splitted:

        new_string_length = len(text) + len(splits)

        if new_string_length < length:
            text = text + " " + splits
        else:
            text_list.append(text)
            text = splits
    text_list.append(text)

    return text_list


def generate_pdf(new_list, audio_split_times, transcriptions):
    # draw to pdf with time
    canvas = Canvas(file_name + ".pdf", pagesize=A4)
    canvas.setFontSize(20)
    canvas.drawString(2 * cm, 28.5 * cm, "Transkription")
    canvas.setFontSize(10)
    canvas.drawString(2 * cm, 27 * cm,
                      "Automatisch generiertes PDF Dokument. Es können Fehler in der Transkription vorhanden sein.")
    page_size = 26

    for x_function, chunk in enumerate(new_list):

        if page_size < 1.8:
            page_size = 28
            canvas.showPage()
            canvas.setFontSize(10)

        if x_function == 0:
            if len(transcriptions[x_function]) > 80:
                string_list = generate_text_chunks(transcriptions[x_function], 80)

                canvas.drawString(2 * cm, page_size * cm, "{:.2f}".format(new_list[x_function].duration_seconds, 2)
                                  + "; " + "0 : " + str(audio_split_times[0]) + "; " + str(string_list[0]))

                for string_number in range(1, len(string_list)):
                    canvas.drawString(2 * cm, (page_size - (0.6 * string_number)) * cm, str(string_list[string_number]))

                page_size -= 0.6 * len(string_list)
            else:
                canvas.drawString(2 * cm, page_size * cm, "{:.2f}".format(new_list[x_function].duration_seconds, 2)
                                  + "; " + "0 : " + str(audio_split_times[0]) + "; " + str(transcriptions[x_function]))
                page_size -= 0.6

        else:
            if len(transcriptions[x_function]) > 80:
                string_list = generate_text_chunks(transcriptions[x_function], 80)

                canvas.drawString(2 * cm, page_size * cm, "{:.2f}".format(new_list[x_function].duration_seconds, 2)
                                  + "; " + str(audio_split_times[x_function - 1]) + " : " +
                                  str(audio_split_times[x_function]) + "; " + str(string_list[0]))

                for string_number in range(1, len(string_list)):
                    canvas.drawString(2 * cm, (page_size - (0.6 * string_number)) * cm, str(string_list[string_number]))

                page_size -= 0.6 * len(string_list)

            else:
                canvas.drawString(2 * cm, page_size * cm, "{:.2f}".format(new_list[x_function].duration_seconds, 2)
                                  + "; " + str(audio_split_times[x_function - 1]) + " : " +
                                  str(audio_split_times[x_function]) + "; " + str(transcriptions[x_function]))
                page_size -= 0.6

    canvas.save()

start = time.time()

parser = argparse.ArgumentParser()

parser.add_argument('-f', action='store', dest='filename', required=True,
                    help='Name of the file')

parser.add_argument('-l', action='store', dest='language', required=True,
                    help='Set language. Supported is de and en')

parser.add_argument('-d', action='store', dest='dBFS', type=int, default=-25,
                    help='Can be between -16 and -25')

parser.add_argument('-o', action='store', dest='output', default="both",
                    help='Set Output. Can be video, pdf or both')


parser.add_argument('--version', action='version', version='%(prog)s 0.1')

results_parser = parser.parse_args()

# convert to wav
print("read video file")
video = convert_to_wav(results_parser.filename)
language = results_parser.language
output = results_parser.output

file_name = video.filename
file_name = file_name[:-4]

# read wav file
print("split audio file")
chunks, dbfs_function, audio_file = read_wav_file_and_split("testtest.wav")

target_length = 15 * 1000
output_chunks = add_audio_together(chunks, target_length)

test_3 = 0
for split in output_chunks:
    test_3 += split.duration_seconds

# test for to long chunks
fixed_length_audio_list = fix_length_audio(output_chunks, dbfs_function, audio_file, test_3)

test_4 = 0
for split in fixed_length_audio_list:
    test_4 += split.duration_seconds

print("save parts temporarily")
number, list_chunk_length = save_chunks_temporarily(fixed_length_audio_list)
number += 1

# generate list for time start
added_chunk_list = []
for x, value in enumerate(list_chunk_length):
    if x == 0:
        added_chunk_list.append(value)

    else:
        new_value = added_chunk_list[x - 1] + value
        new_value = round(new_value, 2)
        added_chunk_list.append(new_value)

# adding text to video and create video
# create video chunk from the list
clip_list = create_video_chunks(video, number, added_chunk_list)

# create one extra chunk for the last like in pdf creator

# generate text clip
# add text to the video chunk
# add chunks together
print("transcribe parts")
list_transcription = transcribe_snippets(number)

if output == "video":
    print("generate video")
    generate_video(clip_list, list_transcription)
elif output == "pdf":
    print("generate pdf")
    generate_pdf(fixed_length_audio_list, added_chunk_list, list_transcription)
elif output == "both":
    print("generate video")
    generate_video(clip_list, list_transcription)
    print("generate pdf")
    generate_pdf(fixed_length_audio_list, added_chunk_list, list_transcription)
else:
    sys.exit("wrong output format")

# delete temporary files
# delete test_test
for x in range(number):
    path = "test_test" + str(x) + ".wav"
    os.remove(path)
os.remove("testtest.wav")

finish = time.time()
print(datetime.timedelta(seconds=(finish - start)))
