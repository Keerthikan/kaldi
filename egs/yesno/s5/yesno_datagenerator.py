from pynput import keyboard
import time
import pyaudio
import wave
import math

CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WAVE_OUTPUT_FILENAME = "output.wav"



class MyListener(keyboard.Listener):
    def __init__(self):
        super(MyListener, self).__init__(on_press=self.on_press, on_release=self.on_release)
        self.key_pressed = None

    
    def on_press(self, key):
        if key == keyboard.Key.cmd_l:
            self.p = pyaudio.PyAudio()
            self.frames = []

            self.stream = self.p.open(format=FORMAT,
                                 channels=CHANNELS,
                                 rate=RATE,
                                 input=True,
                                 frames_per_buffer=CHUNK,
                                 stream_callback = self.callback)
        
            print ("Stream active? " + str(self.stream.is_active()))
            self.key_pressed = True
    
    def on_release(self, key):
        if key == keyboard.Key.cmd_l:
            self.key_pressed = False

    def callback(self,in_data, frame_count, time_info, status):
        if self.key_pressed == True:
            #stream_queue.put(in_data)
            print("record")
            self.frames.append(in_data)
            return (in_data, pyaudio.paContinue)
    
        elif self.key_pressed == False:
            #stream_queue.put(in_data)
            self.frames.append(in_data)
            return (in_data, pyaudio.paComplete)
    
        else:
            return (in_data,pyaudio.paContinue)



class yesno_generator:
    def __init__(self,pattern_length):
        self.pattern_length = pattern_length
        self.limit = math.pow(2,pattern_length)-1
        self.step = 0
    def begin(self):
        if self.step <= self.limit:
            self.generate_pattern()
    
    def end(self):
        if self.step <= self.limit:
            print self.step
            self.generate_wav()
            self.generate_text()
            self.generate_utt2spk()
            self.step+=1
        else:
            self.generate_spk2utt()

    def generate_pattern(self):
        pattern = '_'.join(bin(self.step)[2:].zfill(self.pattern_length))
        print '_'.join(pattern)
        return '_'.join(pattern)

    def generate_text(self):
        pattern = '_'.join(bin(self.step)[2:].zfill(self.pattern_length))
        pattern_without_underscore = bin(self.step)[2:].zfill(self.pattern_length)
        text = ''
        for x in range(0,self.pattern_length):
            text += ' '
            if pattern_without_underscore[x] == '0':
                text += 'NO'
            if pattern_without_underscore[x] == '1':
                text += 'YES'
        text += '\n'
        output = pattern + text
        FileSave('text',output)

    def generate_utt2spk(self):
        pattern = '_'.join(bin(self.step)[2:].zfill(self.pattern_length))
        output = pattern + ' ' + 'Kiddi' + '\n'
        FileSave('utt2spk',output)

    def generate_spk2utt(self):
        output = '\n' + 'Kiddi'
        for x in range(0,self.pattern_length):
            pattern = '_'.join(bin(x)[2:].zfill(self.pattern_length))
            output += ' ' + pattern
        FileSave('spk2utt',output)


    def generate_wav(self):
        pattern = '_'.join(bin(self.step)[2:].zfill(self.pattern_length))
        output = pattern + ' ' + 'location' + '\n'
        FileSave('wav.scp',output)


def FileSave(filename,content):
    with open(filename, "a") as myfile:
        myfile.write(content)

listener = MyListener()
datagen = yesno_generator(4)
listener.start()
started = False



while True:
    time.sleep(0.1)
    if listener.key_pressed == True and started == False:
        started = True
        datagen.begin()
        listener.stream.start_stream()
        print ("Start stream -  Key is down")


    elif listener.key_pressed == False and started == True:
        datagen.end()
        print("Key has been released")
        listener.stream.stop_stream()
        listener.stream.close()
        print("stream has been closed")
        listener.p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(listener.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(listener.frames))
        wf.close()

        started = False

