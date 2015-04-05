# -*- coding: utf-8 -*-
class MediaParser(object):
    @staticmethod
    def is_valid_format(fmt):
        return fmt.get('ext', None) == 'mp4' and fmt.get('url', '').startswith('http')

    def is_valid_video(self, obj):
        raise NotImplementedError('VideoParser.is_valid_video() must be implemented!')

    def parse(self, obj):
        return {
            'title': obj.get('title', ''),
            'thumbnail': obj.get('thumbnail', ''),
            'description': obj.get('description', ''),
            'reference': obj.get('webpage_url', '')
        }


class NaverVideoParser(MediaParser):
    def parse(self, obj):
        candidates = filter(MediaParser.is_valid_format, obj.get('formats', []))
        fmts = {(str(fmt['height']) + 'p'): fmt['url'] for fmt in candidates}

        return dict(super().parse(obj), **{
            'type': 'video',
            'provider': 'naver',
            'formats': fmts
        })

    def is_valid_video(self, obj):
        return obj.get('extractor_key', '').lower() == 'naver'


class FacebookVideoParser(MediaParser):
    RES_MAP = {'sd': '480p', 'hd': '720p'}

    def parse(self, obj):
        candidates = filter(MediaParser.is_valid_format, obj.get('formats', []))
        fmts = {self.RES_MAP[fmt['format_id']]: fmt['url'] for fmt in candidates}

        return dict(super().parse(obj), **{
            'type': 'video',
            'provider': 'facebook',
            'formats': fmts
        })

    def is_valid_video(self, obj):
        return obj.get('extractor_key', '').lower() == 'facebook'


class VimeoVideoParser(MediaParser):
    def parse(self, obj):
        candidates = filter(MediaParser.is_valid_format, obj.get('formats', []))
        fmts = {(str(fmt['height']) + 'p'): fmt['url'] for fmt in candidates}

        return dict(super().parse(obj), **{
            'type': 'video',
            'provider': 'vimeo',
            'formats': fmts
        })

    def is_valid_video(self, obj):
        return obj.get('extractor_key', '').lower() == 'vimeo'


class YoutubeVideoParser(MediaParser):
    def parse(self, obj):
        candidates = filter(MediaParser.is_valid_format, obj.get('formats', []))
        fmts = {(str(fmt['height']) + 'p'): fmt['url'] for fmt in candidates}

        return dict(super().parse(obj), **{
            'type': 'video',
            'provider': 'youtube',
            'formats': fmts
        })

    def is_valid_video(self, obj):
        return obj.get('extractor_key', '').lower() == 'youtube'


class SoundCloudAudioParser(MediaParser):
    @staticmethod
    def is_valid_format(fmt):
        return fmt.get('ext', None) == 'mp3' and fmt.get('url', '').startswith('http')

    def parse(self, obj):
        candidates = filter(SoundCloudAudioParser.is_valid_format, obj.get('formats', []))
        fmts = {fmt['format_id']: fmt['url'] for fmt in candidates}
        return dict(super().parse(obj), **{
            'type': 'audio',
            'provider': 'soundcloud',
            'formats': fmts
        })

    def is_valid_video(self, obj):
        return obj.get('extractor_key', '').lower() == 'soundcloud'


PARSERS = {
    'naver': NaverVideoParser(),
    'facebook': FacebookVideoParser(),
    'vimeo': VimeoVideoParser(),
    'youtube': YoutubeVideoParser(),
    'soundcloud': SoundCloudAudioParser()
}
