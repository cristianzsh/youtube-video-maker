#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

class VideoRobot():

    def __init__(self, project_directory):
        self.images_directory = project_directory
        self.subtitles_template = """
1
00:00:00,000 --> 00:00:10,000
{0}

2
00:00:10,000 --> 00:00:20,000
{1}

3
00:00:20,000 --> 00:00:30,000
{2}

4
00:00:30,000 --> 00:00:40,000
{3}

5
00:00:40,000 --> 00:00:50,000
{4}

6
00:00:50,000 --> 00:01:00,000
{5}

7
00:01:00,000 --> 00:01:10,000
{6}"""

    def make_video(self):
        command = "cat {0}/*.jpg | ffmpeg -y -framerate 0.08 -f image2pipe -i - {0}/output_imgs.mp4".format(self.images_directory)

        os.system(command)

    def add_subtitles(self, sentences):
        self.subtitles_template = self.subtitles_template.format(sentences[0],
            sentences[1], sentences[2], sentences[3],
            sentences[4], sentences[5], sentences[6])

        with open("{0}/subtitles.srt".format(self.images_directory), "w") as subtitles_file:
            subtitles_file.write(self.subtitles_template)

        os.system("ffmpeg -y -i {0}/output_imgs.mp4 -vf subtitles={0}/subtitles.srt {0}/output_text.mp4".format(self.images_directory))

    def add_music(self):
        os.system("ffmpeg -y -i {0}/output_text.mp4 -i music.ogg -c copy -map 0:v:0 -map 1:a:0 {0}/final_video.mp4".format(self.images_directory))
