# from math import *
from random import choice
# from time import *
from pathlib import Path
from data import Database
import pygame


class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        db = Database()
        # Boolean data
        self.is_mute = False
        self.is_loop = False                                                    # Repeat music endlessly
        # Main data
        self.path_sound =   db.PATH_SOUND
        self.path_music =   db.PATH_MUSIC
        self.EntityNames =  db.ENTITYNAMES
        self.NamesS = [f.name for f in Path(self.path_sound).glob(f"*{db.MUSIC_FORMAT}")]
        self.NamesM = [f.name for f in Path(self.path_music).glob(f"*{db.MUSIC_FORMAT}")]
        # Volume data
        self.sound_volume = 0.1
        self.music_volume = 0.5
        # Sounds & musics data
        self.sound_name = None
        self.music_name = None
        self.current_sound: pygame.mixer.Sound = None
        self.current_music: pygame.mixer.Sound = None
        self.Sounds = {}                                                        # All sounds
        self.Musics = {}                                                        # All musics
        # Based functions
        self.create_sounds()
        self.create_musics()

    def create_sounds(self):                                                    # Load and add all sounds when called
        for name in self.NamesS:
            self.Sounds[name] = pygame.mixer.Sound(Path(self.path_sound) / name)

    def create_musics(self):                                                    # Load and add all sounds when called
        for name in self.NamesM:
            self.Musics[name] = pygame.mixer.Sound(Path(self.path_music) / name)

    def check_volumes(self):                                                    # Check if volume is correct
        self.music_volume = max(min(self.music_volume, 1), 0)
        self.sound_volume = max(min(self.sound_volume, 1), 0)

    def get_type_of_sounds(self, name):                                         # Return a list of specific sounds
        return [k for k, _ in self.Sounds.items() if name in k]

    def play_entity_sound(self, name):                                          # Use to make entity play random sounds
        Sounds = self.get_type_of_sounds(name)
        if len(Sounds) > 0:
            sound = choice(Sounds)
            self.play_sound(sound)

    def is_sound_playing(self, name):                                           # Get if given sound is playing
        if name in self.Sounds.keys():
            if self.Sounds[name]:
                return self.Sounds[name].get_num_channels()
            return False
        return False

    def set_volume(self, new_value):                                            # Change volume value
        self.sound_volume = new_value
        self.check_volumes()
        if self.current_sound:
            self.current_sound.set_volume(self.sound_volume)

    def increase_volume(self):                                                  # Add 10% volume value
        self.sound_volume += 0.05
        self.set_volume(self.sound_volume)

    def reduce_volume(self):                                                    # Reduce 10% volume value
        self.sound_volume -= 0.05
        self.set_volume(self.sound_volume)

    def set_music_volume(self, new_value):                                      # Change music volume value
        self.music_volume = new_value
        self.check_volumes()
        if self.current_music:
            self.current_music.set_volume(self.music_volume)

    def increase_music_volume(self):                                            # Add 10% music volume value
        self.music_volume += 0.05
        self.set_music_volume(self.music_volume)

    def reduce_music_volume(self):                                              # Reduce 10% music volume value
        self.music_volume -= 0.05
        self.set_music_volume(self.music_volume)

    def play_sound(self, name, loops=0):                                        # Play given sound
        if name in self.Sounds.keys():
            self.sound_name = name
            self.current_sound = self.Sounds[name]
            self.current_sound.play(loops=loops)
            self.current_sound.set_volume(self.sound_volume)

    def stop_sound(self, name=None):                                            # Stop given sound
        if name in self.Sounds.keys():
            self.Sounds[name].stop()
        elif self.current_sound:
            self.current_sound.stop()

    def play_music(self, name=None, loops=0):                                   # Play given music
        loops = -1 if self.is_loop else loops
        if name is None and len(self.Musics.values()) > 0:
            self.stop_music()
            name = choice(list(self.Musics.keys()))                             # Random music
            self.music_name = name
            self.current_music = self.Musics[name]
            self.current_music.play(loops=loops)
            self.current_music.set_volume(self.music_volume)
        elif name in self.Musics.keys():
            self.stop_music()
            self.music_name = name
            self.current_music = self.Musics[name]
            self.current_music.play(loops=loops)
            self.current_music.set_volume(self.music_volume)

    def stop_music(self):                                                       # Stop given sound
        if self.current_music:
            self.current_music.stop()

    def stop_all_sounds(self):                                                  # Stop all sounds playing
        if self.is_mute:
            pygame.mixer.init()
            if self.current_music:                                              # Play current music again
                loops = -1 if self.is_loop else 0
                self.current_music.play(loops)
                self.current_music.set_volume(self.music_volume)
        else:
            pygame.mixer.stop()
        self.is_mute = not self.is_mute
