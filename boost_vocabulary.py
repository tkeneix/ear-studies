import sys
import argparse
import csv
import os
from google.cloud import texttospeech
from pydub import AudioSegment
from mutagen.easyid3 import EasyID3


def synthesize_audio(
        input_en_path,
        input_jp_path,
        loop_count,
        output_path,
        option):
    loop_max = int(loop_count.strip())

    audio_en = AudioSegment.from_mp3(input_en_path)
    audio_jp = AudioSegment.from_mp3(input_jp_path)

    opening_margin = AudioSegment.silent(duration=100)
    between_sentences = AudioSegment.silent(duration=option.between_sentences)
    between_the_loop = AudioSegment.silent(duration=option.between_the_loop)

    if option.japanese_top:
        audio = opening_margin + audio_jp + between_sentences + audio_en
        if loop_max > 1:
            for li in range(loop_max - 1):
                audio += between_the_loop + audio_jp + between_sentences + audio_en
    else:
        audio = opening_margin + audio_en + between_sentences + audio_jp
        if loop_max > 1:
            for li in range(loop_max - 1):
                audio += between_the_loop + audio_en + between_sentences + audio_jp

    audio.export(output_path, format='mp3')
    os.remove(input_en_path)
    os.remove(input_jp_path)


def create_audio(
        output_path,
        text,
        params_language_code,
        params_name,
        params_speaking_rate):
    client = texttospeech.TextToSpeechClient.from_service_account_json(
        option.servicekey_of_file)
    s_input = texttospeech.types.SynthesisInput(text=text)
    voice_params = texttospeech.types.VoiceSelectionParams(
        language_code=params_language_code, name=params_name)
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3,
        speaking_rate=params_speaking_rate)
    response = client.synthesize_speech(
        s_input, voice_params, audio_config)
    with open(output_path, 'wb') as out:
        out.write(response.audio_content)


def set_id3tag(output_path, artist, album, title):
    id3tag = EasyID3(output_path)
    id3tag["title"] = title
    id3tag["artist"] = artist
    id3tag["album"] = album
    id3tag.save()


def parse_argument():
    # 引数解析
    parser = argparse.ArgumentParser(
        description='Google Text to Speechを使用してテキストからmp3ファイルを生成します。音声は英語から日本語の順番に発声します。')
    parser.add_argument('-f', '--file_of_path',
                        action='store',
                        nargs=None,
                        const=None,
                        required=True,
                        default=None,
                        type=str,
                        help='テキストの記述されたファイルのパスを指定します',
                        metavar=None)
    parser.add_argument('-k', '--servicekey_of_file',
                        action='store',
                        nargs=None,
                        const=None,
                        required=True,
                        default=None,
                        type=str,
                        help='サービスアカウントのキーが記述されたファイル(.json)のパスを指定します',
                        metavar=None)
    parser.add_argument('-t', '--japanese_top',
                        action='store_true',
                        required=False,
                        default=False,
                        help='日本語->英語の順に発声する'
                        )
    parser.add_argument('-e', '--english_speaking_rate',
                        action='store',
                        nargs=None,
                        const=None,
                        required=False,
                        default=1.0,
                        type=float,
                        choices=None,
                        help='英語の読み上げる速さ',
                        metavar=None)
    parser.add_argument('-j', '--japanese_speaking_rate',
                        action='store',
                        nargs=None,
                        const=None,
                        required=False,
                        default=1.5,
                        type=float,
                        choices=None,
                        help='日本語の読み上げる速さ',
                        metavar=None)
    parser.add_argument('-s', '--between_sentences',
                        action='store',
                        nargs=None,
                        const=None,
                        required=False,
                        default=500,
                        type=int,
                        choices=None,
                        help='英語と日本語の発声を読み上げる間隔(msec)',
                        metavar=None)
    parser.add_argument('-l', '--between_the_loop',
                        action='store',
                        nargs=None,
                        const=None,
                        required=False,
                        default=1000,
                        type=int,
                        choices=None,
                        help='センテンスを繰り返す際の間隔(msec)',
                        metavar=None)
    parser.add_argument('-r', '--delimiter',
                        action='store',
                        nargs=None,
                        const=None,
                        required=False,
                        default=",",
                        type=str,
                        help='テキストファイルのCSVおけるデリミタを指定する',
                        metavar=None)

    option = parser.parse_args(sys.argv[1:])
    return option


if __name__ == '__main__':
    option = parse_argument()

    with open(option.file_of_path, 'r') as fi:
        reader = csv.reader(fi, delimiter=option.delimiter)

        # ファイルフォーマットとしてヘッダがあることを期待し読み飛ばします
        # flag[y|n], Id3tag_artist, Id3tag_album, Id3tag_title, english, japanese, output_path, loop_count
        next(reader)
        for row in reader:
            onoff_flag = row[0]
            id3tag_artist = row[1]
            id3tag_album = row[2]
            id3tag_title = row[3]
            english = row[4]
            japanese = row[5]
            output_path = row[6]
            loop_count = row[7]

            if onoff_flag == "y":
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                input_en_path = output_path + ".en"
                input_jp_path = output_path + ".jp"
                create_audio(
                    input_en_path,
                    english,
                    'en-US',
                    'en-US-Wavenet-D',
                    option.english_speaking_rate)
                create_audio(
                    input_jp_path,
                    japanese,
                    'ja-JP',
                    'ja-JP-Wavenet-D',
                    option.japanese_speaking_rate)
                synthesize_audio(
                    input_en_path,
                    input_jp_path,
                    loop_count,
                    output_path,
                    option)
                set_id3tag(output_path, id3tag_artist, id3tag_album, id3tag_title)

                print(output_path)

    print("finished")
