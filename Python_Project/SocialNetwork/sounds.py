import wave
import struct
import math
import os
import pygame

def generate_tone(filename, frequency, duration, volume=0.5, type='sine'):
    if os.path.exists(filename): return
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            # Apply an envelope (decay) for plucky sound
            env = math.exp(-4 * i / n_samples)
            if type == 'sine':
                sample = volume * env * math.sin(2 * math.pi * frequency * i / sample_rate)
            elif type == 'square':
                sample = volume * env * (1.0 if math.sin(2 * math.pi * frequency * i / sample_rate) > 0 else -1.0)
            
            # Clip
            sample = max(-1.0, min(1.0, sample))
            val = int(sample * 32767.0)
            wav_file.writeframesraw(struct.pack('<h', val))

def init_sounds():
    try:
        pygame.mixer.init()
        generate_tone("click.wav", 600, 0.1, 0.2, 'sine')
        generate_tone("connect.wav", 1200, 0.2, 0.3, 'sine')
        generate_tone("recommend.wav", 800, 0.4, 0.3, 'square')
    except Exception as e:
        print("Audio not initialized:", e)

def play(name):
    try:
        filename = f"{name}.wav"
        if os.path.exists(filename):
            sound = pygame.mixer.Sound(filename)
            sound.set_volume(0.3)
            sound.play()
    except:
        pass
