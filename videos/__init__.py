# -*- coding: utf-8 -*-
import logging
import traceback

from flask import Flask, jsonify, request
from youtube_dl import YoutubeDL, gen_extractors, DownloadError
from youtube_dl.version import __version__ as youtube_dl_version
from youtube_dl.utils import ExtractorError
from .parser import PARSERS


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


class VideosDL(YoutubeDL):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_default_info_extractors()


def build_result(result):
    r_type = result.get('_type', 'video')
    media = []
    if r_type == 'video':
        media = [PARSERS[result['extractor_key'].lower()].parse(result)]
    elif r_type == 'playlist':
        for entry in result['entries']:
            media.extend(build_result(entry))
    elif r_type == 'compat_list':
        for r in result['entries']:
            media.extend(build_result(r))
    return media


@app.route('/extractors')
def get_extractors():
    extractors = [dict(name=ie.IE_NAME, working=ie.working()) for ie in gen_extractors()]
    return jsonify(extractors=extractors, dl_version=youtube_dl_version)


@app.route('/media')
def get_media():
    url = request.args.get('url', None)
    if not url:
        return jsonify(error_code=400, message='Bad Request (url must be required!)',
                       dl_version=youtube_dl_version), 400

    dl_params = {
        'cachedir': False,
        'logger': app.logger.getChild('youtube-dl')
    }

    try:
        with VideosDL(dl_params) as dl:
            result = dl.extract_info(url, download=False)

        return jsonify(media=build_result(result))
    except (DownloadError, ExtractorError) as e:
        logging.error(traceback.format_exc())
        return jsonify(error_code=500, message='Download failed', exception=e, dl_version=youtube_dl_version), 500
