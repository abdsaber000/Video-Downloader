from call_params import CallParams
import yt_dlp as youtube_dl
import helper
from enums import DownloadType
class DownloadMeta:
    def __init__(self, format : dict, download_type = DownloadType.NORMAL):
        self.format_id = format.get('format_id')
        self.mixed_audio_id = None
        self.mixed_audio_filesize = 0
        self.filesize = format.get('filesize')
        self.ext = format.get('ext')
        self.resolution = format.get('resolution')
        self.download_type = download_type

    def add_audio_format(self, format : dict) -> None:
        if self.mixed_audio_id == None:
            self.mixed_audio_id = format.get('format_id')
            self.mixed_audio_filesize = format.get('filesize')
            if self.filesize != None:
                self.filesize += self.mixed_audio_filesize
        else:
            self.mixed_audio_id = format.get('format_id')
            old_mixed_audio_filesize = self.mixed_audio_filesize
            self.mixed_audio_filesize = format.get('filesize')
            if self.filesize != None:
                self.filesize -= old_mixed_audio_filesize
                self.filesize += self.mixed_audio_filesize
            
    def get_formats_list(self) -> list:
        result = [self.format_id]
        if self.download_type == DownloadType.MIXED_AUDIO:
            result.append(self.mixed_audio_id)
        return result
    
    def __str__(self) -> str:
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
    
    def download_format_option(format_ids_list : list, output_ext : str, progress_hook):
        return {
            'format' : helper.get_download_list_to_str(format_ids_list),
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': output_ext,
            }],
            'external_downloader': 'axel',  # Specify axel as the external downloader
            'external_downloader_args': ['-n', '10', '-a'],  # Arguments for axel
            'verbose' : True,
            'progress_hooks': [progress_hook]
        }


class Downloader:
    def __init__(self, call_params : CallParams):
        self.download_list : list[DownloadMeta] = []
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
            audio_formats_list = [] # this list is temp until better audio selection policy is found
            for format in formats:
                audio_codec = format.get('acodec')
                if format.get('resolution') == 'audio only':
                    audio_formats_list.append(format)
                if audio_codec == 'none':
                    self.download_list.append(DownloadMeta(format, DownloadType.VIDEO_ONLY))
                    self.download_list.append(DownloadMeta(format, DownloadType.MIXED_AUDIO))
                else:
                    self.download_list.append(DownloadMeta(format))
            for download_meta in self.download_list:
                if download_meta.download_type == DownloadType.MIXED_AUDIO:
                    download_meta.add_audio_format(audio_formats_list[-1])
        return self.get_search_list_summary()
    
    def download_video(self, url, format_index):
        format_ids_list = self.download_list[format_index].get_formats_list()
        output_ext = self.download_list[format_index].ext
        with youtube_dl.YoutubeDL(YoutubeDlOptions.download_format_option(format_ids_list, output_ext, self.my_hook)) as ydl:
            ydl.download([url])
        
    def my_hook(self, d):
        self.call_params.update_params(d)