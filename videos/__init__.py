# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from youtube_dl import YoutubeDL, gen_extractors


app = Flask(__name__)


class VideosDL(YoutubeDL):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_default_info_extractors()


@app.route('/extractors')
def get_extractors():
    extractors = [dict(name=ie.IE_NAME, working=ie.working()) for ie in gen_extractors()]
    return jsonify(extractors=extractors)
