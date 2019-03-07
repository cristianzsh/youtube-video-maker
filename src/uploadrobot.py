#!/usr/bin/python
# -*- coding: utf-8 -*-

import http.client as httplib
import httplib2
import os
import random
import sys
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

class UploadRobot():

    def __init__(self):
        httplib2.RETRIES = 1
        self.MAX_RETRIES = 10

        self.RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
            httplib.IncompleteRead, httplib.ImproperConnectionState,
            httplib.CannotSendRequest, httplib.CannotSendHeader,
            httplib.ResponseNotReady, httplib.BadStatusLine)

        self.RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
        self.CLIENT_SECRETS_FILE = "client_secrets.json"

        self.YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
        self.YOUTUBE_API_SERVICE_NAME = "youtube"
        self.YOUTUBE_API_VERSION = "v3"
        self.MISSING_CLIENT_SECRETS_MESSAGE = """
        WARNING: Please configure OAuth 2.0

        To make this sample run you will need to populate the client_secrets.json file
        found at:

           %s

        with information from the Developers Console
        https://console.developers.google.com/

        For more information about the client_secrets.json file format, please visit:
        https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
        """ % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           self.CLIENT_SECRETS_FILE))

    def get_authenticated_service(self, args):
        flow = flow_from_clientsecrets(self.CLIENT_SECRETS_FILE,
            scope = self.YOUTUBE_UPLOAD_SCOPE,
            message = self.MISSING_CLIENT_SECRETS_MESSAGE)

        storage = Storage("%s-oauth2.json" % sys.argv[0])
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage, args)

        return build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
            http = credentials.authorize(httplib2.Http()))

    def initialize_upload(self, youtube, options):
        tags = None
        if options.keywords:
            tags = options.keywords.split(",")

        body = dict(
            snippet = dict(
                title = options.title,
                description = options.description,
                tags = tags,
                categoryId = options.category
            ),

            status = dict(
                privacyStatus = options.privacy_status
            )
        )

        insert_request = youtube.videos().insert(
            part = ",".join(body.keys()),
            body = body,
            media_body = MediaFileUpload(options.file, chunksize = -1, resumable = True)
        )

        self.resumable_upload(insert_request)

    def resumable_upload(self, insert_request):
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                status, response = insert_request.next_chunk()
                if "id" in response:
                    print("[*] Video id '%s' was successfully uploaded." % response["id"])
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
            except HttpError as e:
                if e.resp.status in self.RETRIABLE_STATUS_CODES:
                    error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                 e.content)
                else:
                    raise
            except self.RETRIABLE_EXCEPTIONS as e:
                error = "A retriable error occurred: %s" % e

            if error is not None:
                print(error)
                retry += 1
                if retry > self.MAX_RETRIES:
                    exit("No longer attempting to retry.")

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print("Sleeping %f seconds and then retrying..." % sleep_seconds)
                time.sleep(sleep_seconds)
