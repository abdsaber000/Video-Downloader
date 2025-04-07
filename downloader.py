from call_params import CallParams
import yt_dlp as youtube_dl
import helper
from enums import DownloadType
class DownloadMeta:
    def __init__(self, format : dict, download_type = DownloadType.NORMAL):
        self.format_id = format.get('format_id')
        self.filesize = format.get('filesize')
        self.ext = format.get('ext')
        self.resolution = format.get('resolution')
        self.download_type = download_type

    def __str__(self):
        summary =  str(self.resolution) + ' ' + str(self.ext) + ' ' + str(helper.convert_size_to_string(self.filesize))
        if self.download_type == DownloadType.VIDEO_ONLY:
            summary = summary + ' (video only)'
        elif self.download_type == DownloadType.MIXED_AUDIO:
            summary = summary + ' (mixed audio)'
        return summary

class YoutubeDlOptions:
    def search_for_formats_option():
        return {
            'listformats': True,
            'quiet': True
        }
    
    def download_format_option(format_id : int, progress_hook):
        return {
            'format' : format_id,
            'external_downloader': 'axel',  # Specify axel as the external downloader
            'external_downloader_args': ['-n', '10', '-a'],  # Arguments for axel
            'verbose' : True,
            'progress_hooks': [progress_hook]
        }


class Downloader:
    def __init__(self, call_params : CallParams):
        self.download_list = []
        self.call_params = call_params
        self.search_result = []
    def clear_download_list(self):
        self.download_list.clear()
    
    def get_search_list_summary(self):
        result = []
        for format in self.download_list:
            result.append(str(format))
        return result

    def search_for_video_formats(self, url):
        with youtube_dl.YoutubeDL(YoutubeDlOptions.search_for_formats_option()) as ydl:
            meta = ydl.extract_info(url, download=False)
            formats = meta.get('formats', [meta])
            for format in formats:
                audio_codec = format.get('acodec')
                if audio_codec == 'none':
                    self.download_list.append(DownloadMeta(format, DownloadType.VIDEO_ONLY))
                    self.download_list.append(DownloadMeta(format, DownloadType.MIXED_AUDIO))
                else:
                    self.download_list.append(DownloadMeta(format))
        return self.get_search_list_summary()
    
    def download_video(self, url, format_index):
        format_id = self.download_list[format_index].format_id
        with youtube_dl.YoutubeDL(YoutubeDlOptions.download_format_option(format_id, self.my_hook)) as ydl:
            ydl.download([url])
        
    def my_hook(self, d):
        self.call_params.update_params(d)