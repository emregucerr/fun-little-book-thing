import json


videos = []

for i in range(73):
    v = {
    'id': str(i),
    'url': f'https://fume.b-cdn.net/books/the-art-of-war/{i}.mp4',
    'title': f'Video {i}',
    'author': 'Hattori Hanzo',
    'thumbnail': f'https://fume.b-cdn.net/books/the-art-of-war/thumbnail_{i}.png'
    }
    videos.append(v)

with open('videos.json', 'w') as f:
    json.dump(videos, f)