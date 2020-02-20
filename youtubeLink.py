__module_name__ = "youtubeLink" 
__module_version__ = "1.2" 
__module_description__ = "Displays information about YouTube videos linked in chat"

##
##      Youtube link script for Hexchat
##      by Cycloneblaze and Galaxy
##
##      version history
##      1.0 - based on Galaxy's Youtube script v1.3
##          - new API key
##          - new video message incl. channel name
##      1.1 - formatting numbers
##      1.2 - now supports multiple channels
##          - the script will activate in any channel you are in with a
##          name that is in the channel variable. add names separated with
##          commas and surrounded in quotes.
##
##      todo: refactor code and stuff
##

import hexchat
from apiclient.discovery import build
from apiclient.errors import HttpError

youtube = build("youtube", "v3", developerKey="AIzaSyDXWnobaSQlppM_2iG9QwoCEoln90l5lgs")
vid_id = ''
channel = ('#gtsplus', '#gundam')

hexchat.prnt("{} script v{} loaded. python code by Cycloneblaze".format(__module_name__, __module_version__))
def unload_cb(userdata):
    hexchat.prnt("{} script v{} unloaded".format(__module_name__, __module_version__))

def link_type(message):

    if "://www.youtube.com/watch?v=" in message[1]:
        start = message[1].find('watch?v=')
        vid_id = message[1][start+8:start+19]
    elif "://youtu.be/" in message[1]:
        start = message[1].find('.be/')
        vid_id = message[1][start+4:start+15]

    return vid_id


def youtube_cb(word, word_eol, userdata): 

    if hexchat.get_info('channel') == channel:
        current_channel = if hexchat.get_info('channel')

        if ("://www.youtube.com/watch?v=" in word[1]) or ("://youtu.be/" in word[1]):
            vid_id = link_type(word)
            vid = youtube.videos().list(id=vid_id, part='snippet, contentDetails, statistics').execute()
            vid_dur = 'hour:minute:second'

            for vid_res in vid.get("items", []):
                vid_title = ("{}".format(vid_res['snippet']['title']))
                vid_time = ("{}".format(vid_res['contentDetails']['duration'])[2:])
                vid_channel = ("{}".format(vid_res['snippet']['channelTitle']))
                vid_date = ("{}".format(vid_res['snippet']['publishedAt']))
                vid_views = ("{}".format(vid_res['statistics']['viewCount']))
                vid_likes = ("{}".format(vid_res['statistics']['likeCount']))
                vid_dislikes = ("{}".format(vid_res['statistics']['dislikeCount']))

                hours=minutes=seconds=True

                if "H" not in vid_time:
                    vid_dur = vid_dur.replace('hour:','')
                    hours = False
                if "S" not in vid_time:
                    vid_dur = vid_dur.replace('second','00')
                    seconds = False
                if "M" not in vid_time:
                    if not hours and seconds:
                        vid_dur = vid_dur.replace('minute','0')
                        minutes = False
                    else:
                        vid_dur = vid_dur.replace('minute','00')
                        minutes = False

                if hours:
                    vid_dur = vid_dur.replace('hour',vid_time[0])
                    vid_time = vid_time[2:]

                if minutes:
                    start = vid_time.find('M')
                    if (start - 1):
                        vid_dur = vid_dur.replace('minute',vid_time[:2])
                        vid_time = vid_time[3:]
                    else:
                        if not hours:
                            vid_dur = vid_dur.replace('minute',vid_time[0])
                            vid_time = vid_time[2:]
                        else:
                            vid_dur = vid_dur.replace('minute',('0' + vid_time[0]))
                            vid_time = vid_time[2:]

                if seconds:
                    if len(vid_time) == 3:
                        vid_dur = vid_dur.replace('second',vid_time[0:2])
                    else:
                        vid_dur = vid_dur.replace('second',('0' + vid_time[0]))

                vid_views = int(vid_views)
                vid_views = '{:,}'.format(vid_views)

                vid_likes = int(vid_likes)
                vid_likes = '{:,}'.format(vid_likes)

                vid_dislikes = int(vid_dislikes)
                vid_dislikes = '{:,}'.format(vid_dislikes)

                pos = vid_date.find('T')
                vid_date = vid_date[:pos]

                if vid_title not in word[1]:
                    hexchat.command("bs say {} {} [{}] [Uploaded by {}]".format(current_channel, vid_title, vid_dur, vid_channel))

    return hexchat.EAT_NONE

EVENTS = [("Channel Message"),("Your Message"),("Your Action"),("Channel Action"),("Channel Msg Hilight")]
for event in EVENTS:
    hexchat.hook_print(event, youtube_cb)
hexchat.hook_unload(unload_cb)
