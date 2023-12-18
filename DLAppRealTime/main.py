import pyaudio
import numpy as np
import time
import array
import queue
from kss_raw import Keyword_Spotting_Service
import pyqtgraph as pg
import sys
import scipy.io.wavfile
import wave
import keyboard
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt

TEST_AUDIO_FILE_PATH = "./test/left.wav"
SAMPLE_RATE = 22050
CHUNK = int(SAMPLE_RATE / 10)
CHUNK_MEL = 22050  # 推定したい音の長さに合わせる。1秒=sample_rate


class PlotWindow:
    def __init__(self):
        self.fig, (self.ax1) = plt.subplots(1, 1, figsize=(12, 8))
        # self.ax1.plot([1,2,3], [3,4,5])

    def update(self, xdata, ydata):
        plt.cla()
        buf = convert_buffer(ydata)
        self.ax1.plot(xdata, buf)
        plt.pause(0.01)
        # plt.show()


# # 使用する推論を代入
# def setPredictor(self, predictor):
#     self.pred = predictor
pred_buffer = []
rec_bin_buffer = bytearray()  # binaryのままにする


def convert_buffer(buffer):
    return np.array(pred_buffer) / 32768.0


class AudioInputStream:
    def __init__(self):
        # マイクインプット設定
        self.CHUNK = CHUNK  # 1度に読み取る音声のデータ幅
        self.audio = pyaudio.PyAudio()
        self.audio_buffer_data = []  # 推論用の配列
        self.channel = 1
        self.rate = SAMPLE_RATE
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channel,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.CHUNK,
            stream_callback=self.update,
        )

    def recordOnce(self, filename, data):
        self.wavefile = self._prepare_file(filename)
        self.wavefile.writeframes(data)
        self.wavefile.close()

    def _prepare_file(self, fname="rec_test.wav", mode="wb"):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channel)
        wavefile.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile

    # 音声を取り込む度に実行する関数
    # 音声取り込み => 推論用のAudio配列にFIFOで挿入 => 推論して結果を表示
    def update(self, in_data, frame_count, time_info, status):
        # 録音テスト
        # if keyboard.is_pressed("r"):
        #     self.wavefile.writeframes(in_data)

        # print(in_data[:10])
        global pred_buffer
        # 0. 取得したデータを16進数で配列化
        wave = array.array("h", in_data)
        # # 1. 取得したデータを配列に追加
        pred_buffer.extend(wave)
        # 2. 超えている場合、最初のCHUNK分を削除
        if len(pred_buffer) > CHUNK_MEL:
            # print(f"buf len before: {len(pred_buffer)}")
            del pred_buffer[:CHUNK]
            # print(f"buf len after: {len(pred_buffer)}")

        # global kss
        # buf = np.array(pred_buffer) / 32768.0
        # predicted_keyword = kss.predict(buf, SAMPLE_RATE)
        # print(f"Predicted keyword is: {predicted_keyword}")

        # 音声記録用
        # global rec_bin_buffer
        # rec_bin_buffer.extend(in_data)
        # if len(rec_bin_buffer) > CHUNK_MEL:
        #     print(f"buf len before: {len(rec_bin_buffer)}")
        #     # rec_bin_buffer[0:CHUNK] = b''
        #     rec_bin_buffer = rec_bin_buffer[CHUNK:]
        #     print(f"buf len after: {len(rec_bin_buffer)}")

        return (None, pyaudio.paContinue)


if __name__ == "__main__":
    # pro_size = 10
    # for i in range(1, pro_size + 1):
    #     pro_bar = ('=' * i) + (' ' * (pro_size - i))
    #     print('\r[{0}] {1}%'.format(pro_bar, i / pro_size * 100.), end='')
    #     time.sleep(0.5)

    ############## mein loop ###################

    win = PlotWindow()
    # i = 0
    # while 1:
    #     win.update([0, 1, 2], [i, i+1, i+2])
    #     i+=1
    #     time.sleep(1)

    i = 0
    global kss
    kss = Keyword_Spotting_Service()
    ditect = ""
    ais = AudioInputStream()
    # グラフ描画用
    xdata = np.linspace(0, CHUNK_MEL, CHUNK_MEL)
    while ais.stream.is_active():
        # ais.recordOnce('./wav/rec_{}.wav'.format(i), rec_bin_buffer)

        if len(pred_buffer) == CHUNK_MEL:
            win.update(xdata, pred_buffer)
            
            buf = convert_buffer(pred_buffer)
            predicted_keyword = kss.predict(buf, SAMPLE_RATE)
            # print(f"Predicted keyword is: {predicted_keyword}")
            if predicted_keyword == "dog":
                detect = predicted_keyword
            else:
                detect = "____"
            print("\rdetect: {}".format(detect), end="")
        # val = ais.AudioInput()[0]
        # rms = np.sqrt(np.mean(val**2))
        # print("\rVal = {0}".format(rms), end="")

        time.sleep(0.1)  # 推論頻度を決定
        i += 1

    # ais.stream.stop_stream()
    # ais.stream.close()
    # ais.close()

    # predicted_keyword = kss.predict(TEST_AUDIO_FILE_PATH)
    # print(f"Predicted keyword is: {predicted_keyword}")

# python ref/pyqtgraph/dispWave.py

# ################ 予測用の配列抽出部分 #######################
# # きちんとオーバーラップは考慮されている。
# # 0:44100+4410 をメルスペクトログラムに変換
# audio_to_convert = np.array(raw_audio_buffer[:conf.mels_convert_samples]) / 32767
# # 0:4410 を捨てる
# raw_audio_buffer = raw_audio_buffer[conf.mels_onestep_samples:]
# ###########################################################
