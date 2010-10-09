#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import thread
import subprocess

class Player(threading.Thread):
    
    def __init__(self, running, callback):
        threading.Thread.__init__(self)
        self.running = running
        self.callback = callback
        self.playing = False
        self.run_mpg123()
        
    def run_mpg123(self):
        cmd = "mpg123 -R dummy --skip-printing-frames=32".split()
        self.popen = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    def run(self):
        self.main_loop()
        self.popen.kill()
        self.running.clear()
        self.callback()
        
    def main_loop(self):
        while self.running.isSet():
            self.mpg123_response()
    
    def open(self, song):
        if self.playing:
            self.stop()
        self.song = song
        self.mpg123_request("LOAD %s" % self.song.songUrl)
        self.song.play_status = "播放中"
    
    def restart(self):
        self.mpg123_request("LOAD %s" % self.song.songUrl)
        self.song.play_status = "播放中"
        
    def play(self):
        self.mpg123_request("PAUSE")
    
    def pause(self):
        self.mpg123_request("PAUSE")
    
    def stop(self):
        self.mpg123_request("STOP")
        self.song.play_status = ""
        self.song.play_process = 0
        self.playing = False
        
    def quit(self):
        self.mpg123_request("QUIT")

    def seek(self):
        pass
    
    def mpg123_request(self, text):
        self.popen.stdin.write(text)
    
    def mpg123_response(self):        
        line = self.popen.stdout.readline()
        if line.startswith("@F"):
            # @F 417 -417 10.89 0.00
            values = line.split()
            prefix = values[0]
            current_frame = values[1]
            frames_remaining = values[2]
            current_time = values[3]
            time_remaining = values[4]
            self.song.play_process = float(current_time) / float(self.song.duration) * 100
            # mpg123 does not auto stop
            if self.song.play_process > 100:
                self.stop()     
 
    def get_current_song(self):
        return self.song
