
from moviepy.editor import *
from moviepy.config import change_settings

def compress_video(old_video_path, new_video_path):
    # 使用ffmpeg压缩视频
    os.system(f'ffmpeg -i "{old_video_path}" -vcodec libx264 -crf 24 "{new_video_path}"')

def join_and_label_videos(video_path1, video_path2, output_path):
    change_settings({"IMAGEMAGICK_BINARY": r"G:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

    # 加载视频，设置持续时间为10秒
    clip1 = VideoFileClip(video_path1).subclip(0, 10)
    clip2 = VideoFileClip(video_path2).subclip(0, 10)

    # 在视频左上角添加文本标签
    video_name1 = os.path.basename(video_path1)
    video_name2 = os.path.basename(video_path2)

    txt_clip1 = TextClip(video_name1, fontsize=24, color='white')
    txt_clip1 = txt_clip1.set_position(('left', 'top')).set_duration(10)
    
    txt_clip2 = TextClip(video_name2, fontsize=24, color='white')
    txt_clip2 = txt_clip2.set_position(('left', 'top')).set_duration(10)

    # 将文本标签与视频组合
    video_with_label1 = CompositeVideoClip([clip1, txt_clip1])
    video_with_label2 = CompositeVideoClip([clip2, txt_clip2])

    # 将两个视频左右拼接
    final_video = clips_array([[video_with_label1, video_with_label2]])

    # 保存结果
    final_video.write_videofile(output_path, fps=24)
