# -*- coding: utf-8 -*-
import logging
import traceback
import sys

from flask import Flask, jsonify, request
from youtube_dl import YoutubeDL, gen_extractors, DownloadError
from youtube_dl.version import __version__ as youtube_dl_version
from youtube_dl.utils import ExtractorError
from werkzeug.contrib.fixers import ProxyFix

from .parser import PARSERS
from videos.util import crossdomain


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config['JSON_AS_ASCII'] = False

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)

root_logger.addHandler(log_handler)


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
@crossdomain(origin='*')
def get_extractors():
    extractors = [dict(name=ie.IE_NAME, working=ie.working()) for ie in gen_extractors()]
    return jsonify(extractors=extractors, dl_version=youtube_dl_version)


@app.route('/media')
@crossdomain(origin='*')
def get_media():
    url = request.args.get('url', None)
    if not url:
        return jsonify(error_code=400, message='Bad Request (url must be required!)',
                       dl_version=youtube_dl_version), 400

    dl_params = {
        'cachedir': False,
        'source_address': request.remote_addr,
        'logger': app.logger.getChild('youtube-dl')
    }

    try:
        with VideosDL(dl_params) as dl:
            result = dl.extract_info(url, download=False)
        return jsonify(media=build_result(result))
    except (DownloadError, ExtractorError) as e:
        logging.error('DownloadError, Client IP: %s, Exception: %s', request.remote_addr, e)
        try:
            del dl_params['source_address']
            with VideosDL(dl_params) as dl:
                result = dl.extract_info(url, download=False)
            return jsonify(media=build_result(result))
        except (DownloadError, ExtractorError) as e:
            logging.error(traceback.format_exc())
            return jsonify(error_code=500, message='Download failed', dl_version=youtube_dl_version), 500
