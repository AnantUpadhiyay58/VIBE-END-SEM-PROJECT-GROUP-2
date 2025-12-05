#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm
from datetime import datetime
import pandas as pd
import time


API_KEY = "AIzaSyC8kQ1Rc8lOkAAQZDK7x43xifi_V9m3Eic"  # Replace with your API key
youtube = build("youtube", "v3", developerKey=API_KEY)

START_DATE = datetime(2025, 9, 29)
END_DATE = datetime(2025, 11, 23)

queries = [
    "Paresh Rawal Taj Story",
    "The Taj Story controversy",
    "Taj Story poster controversy",
    "Paresh Rawal Taj Mahal",
    "Taj Mahal 22 rooms",
    "Taj Story boycott",
    "The Taj Story trailer",
    "Paresh Rawal controversy 2025"
]


all_video_ids = []

print("🔍 Searching for videos...")
for query in queries:
    try:
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=100,
            type="video"
        ).execute()

        video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
        all_video_ids.extend(video_ids)
        print(f"Found {len(video_ids)} videos for '{query}'")

    except HttpError as e:
        print(f"ouTube API error for '{query}': {e}")

all_video_ids = list(set(all_video_ids))
print(f"\nTotal unique videos found: {len(all_video_ids)}\n")

def get_comments(video_id):
    comments = []
    try:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100,
            textFormat='plainText'
        ).execute()
    except HttpError as e:
        if "commentsDisabled" in str(e):
            print(f" Comments disabled: {video_id}")
        else:
            print(f"Error fetching comments for {video_id}: {e}")
        return comments

    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            published_time = datetime.strptime(comment['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")

            # Filter by date
            if START_DATE <= published_time <= END_DATE:
                comments.append({
                    "video_id": video_id,
                    "author": comment.get('authorDisplayName', 'Unknown'),
                    "text": comment.get('textDisplay', ''),
                    "likeCount": comment.get('likeCount', 0),
                    "publishedAt": published_time.strftime("%Y-%m-%d %H:%M:%S")
                })

        if 'nextPageToken' in response:
            time.sleep(1)
            response = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                pageToken=response['nextPageToken'],
                maxResults=100,
                textFormat='plainText'
            ).execute()
        else:
            break
    return comments

comments_data = []

for vid in tqdm(all_video_ids, desc="Downloading comments"):
    video_comments = get_comments(vid)
    comments_data.extend(video_comments)

df = pd.DataFrame(comments_data)
output_file = "youtube_comments_taj_story_controversy.csv"
df.to_csv(output_file, index=False)

print(f"\nDone! Saved {len(df)} comments between {START_DATE.date()} and {END_DATE.date()}.")
print(f"Output file: {output_file}")
