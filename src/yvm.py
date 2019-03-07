#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
from imagerobot import ImageRobot
from searchrobot import SearchRobot
from videorobot import VideoRobot
from uploadrobot import UploadRobot
from urllib.error import HTTPError

def make_project_directory(search_term):
    try:
        search_term = search_term.replace(" ", "_")
        directory_path = os.path.expanduser("~") + "/{}".format(search_term)
        os.mkdir(directory_path)

        return directory_path
    except OSError:
        print("Creation of the project directory failed.")
        sys.exit(1)

if __name__ == "__main__":
    search_term = input("Wikipedia search term: ")
    if len(search_term) == 0:
        print("Please enter a search term.")
        sys.exit(1)

    print("Avaiable prefixes:\n1. What is\n2. Who is\n3. The history of\n4. Learn more about")
    prefixes = ["What is", "Who is", "The history of", "Learn more about"]
    prefix = input("Prefix: ")
    if not prefix in "1234":
        print("Please enter a prefix.")
        sys.exit(1)

    project_directory = make_project_directory(search_term)
    prefix = prefixes[int(prefix) - 1]

    print("[*] Starting search robot...")
    search_robot = SearchRobot()
    search_result = search_robot.search(search_term)
    keywords_list = search_robot.get_keywords(search_result)
    for i in range(len(search_result)):
        print("[*] Sentence {0}: {1}".format(i + 1, search_result[i]))
        print("[*] Keywords: {0}\n".format(keywords_list[i]))

    print("[*] Starting image robot...")
    image_robot = ImageRobot(project_directory)
    images_list = []
    for keywords in keywords_list:
        img = image_robot.get_image(keywords, search_term)
        images_list.append(img)
        print("[*] Image saved in: " + str(img))

    print("[*] Renaming images...")
    images_list = image_robot.rename_files(images_list)

    print("[*] Converting images to JPG...")
    image_robot.convert_to_jpg(images_list)

    print("[*] Starting video robot...")
    video_robot = VideoRobot(project_directory)
    video_robot.make_video()
    video_robot.add_subtitles(search_result)
    video_robot.add_music()

    print("[*] Starting upload robot...")
    upload_robot = UploadRobot()

    title = prefix + " " + search_term
    description = "\n\n".join(search_result)
    keywords = []

    for i in keywords_list:
        keywords += i

    keywords = ",".join(keywords)

    args = argparse.Namespace(
        auth_host_name =  "localhost",
        auth_host_port = [8080, 8090],
        category = "27",
        description = description,
        file = "{}/final_video.mp4".format(project_directory),
        keywords = keywords,
        logging_level =  "ERROR",
        noauth_local_webserver = False,
        privacy_status = "public",
        title = title)

    youtube = upload_robot.get_authenticated_service(args)

    print("[*] Uploading video...")
    try:
        upload_robot.initialize_upload(youtube, args)
    except HTTPError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

    print("[*] Backup files saved in: " + project_directory)
