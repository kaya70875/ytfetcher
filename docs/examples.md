# Example Use Cases

We created example use cases for you. You can check and get inspired by visiting our [GitHub repository](https://github.com/kaya70875/ytfetcher).

## Searching for Keywords in Channel Transcripts

One common use case is searching for specific keywords or phrases across all videos in a channel. Here's an example:

```python
from ytfetcher import YTFetcher
from ytfetcher.services import JSONExporter

def search_in_channel(handle: str, keyword: str):
    # 1. Initialize using your factory method
    fetcher = YTFetcher.from_channel(
        channel_handle=handle,
        max_results=5
    )

    # 2. Fetch the structured data
    print(f"Searching for '{keyword}' in @{handle}...")
    channel_data = fetcher.fetch_youtube_data()

    matches = []

    # 3. Iterate through your ChannelData models
    for video in channel_data:
        for entry in video.transcripts:
            if keyword.lower() in entry.text.lower():
                matches.append({
                    "video_id": video.video_id,
                    "timestamp": entry.start,
                    "text": entry.text
                })

    # 4. Show off the results
    print(f"Found {len(matches)} matches!")
    for m in matches[:5]: # Show first 5
        print(f"[{m['timestamp']}s] in {m['video_id']}: {m['text']}")

    # 5. Use your JSONExporter to save the findings
    exporter = JSONExporter(
        channel_data=channel_data,
        filename=f"{keyword}_search_results",
        timing=True
    )
    exporter.write()

if __name__ == "__main__":
    search_in_channel("TheOffice", "Dunder Mifflin")
```

## Sentiment Analysis With Youtube Comments

We can use `fetch_with_comments` method to get top comments and use it for **sentiment analysis**.

First install `vaderSentiment` for analysis.

```bash
pip install vaderSentiment
```

Here's the full code:

```py
from ytfetcher import YTFetcher
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def analyze_comments(handle: str):
    # 1. Initialize the fetcher for a specific channel
    fetcher = YTFetcher.from_channel(channel_handle=handle, max_results=3)
    
    # 2. Fetch data WITH comments (using your specific method)
    print(f"Fetching comments from @{handle}...")
    channel_data = fetcher.fetch_with_comments(max_comments=20)

    analyzer = SentimentIntensityAnalyzer()
    stats = {"Positive": 0, "Neutral": 0, "Negative": 0}

    # 3. Process the data
    for video in channel_data:
        print(f"\n--- Analyzing: {video.video_id} ---")
        
        if not video.comments:
            print("No comments found for this video.")
            continue

        for comment in video.comments:
            # Use comment.text as defined in your Comment model
            scores = analyzer.polarity_scores(comment.text)
            compound = scores['compound']

            if compound >= 0.05:
                sentiment = "Positive"
            elif compound <= -0.05:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

            stats[sentiment] += 1
            print(f"[{sentiment}] {comment.author}: {comment.text[:50]}...")

    # 4. Final Summary
    print("\n" + "="*30)
    print(f"OVERALL SENTIMENT FOR @{handle}")
    for label, count in stats.items():
        print(f"{label}: {count}")

if __name__ == "__main__":
    analyze_comments("TheOffice")
```

## The AI-Ready Content Summarizer
This script fetches a video's transcript, **strips out unnecessary timing info,** and combines it with metadata to create a perfectly formatted `.txt` file that you can drop into any AI tool.

```py
from ytfetcher import YTFetcher
from ytfetcher.services import TXTExporter

def prepare_for_ai(video_ids: list[str]):
    # 1. Initialize using the video URL factory
    fetcher = YTFetcher.from_video_ids(video_ids=video_ids)
    
    print(f"Downloading transcript for AI processing...")
    channel_data = fetcher.fetch_youtube_data()

    # 2. Extract the text only for a clean 'context' string
    full_transcript = ""
    for video in channel_data:
        # We join the transcript segments into one clean block of text
        full_transcript = " ".join([t.text for t in video.transcripts])
        title = video.metadata.title if video.metadata else "Unknown Title"

    # 3. Use your TXTExporter with specific settings 
    # We turn off 'timing' to make it readable for an AI
    exporter = TXTExporter(
        channel_data=channel_data,
        filename="ai_context_ready",
        timing=False, 
        allowed_metadata_list=['title', 'url', 'description']
    )
    exporter.write()

    print(f"--- PREVIEW FOR AI ---")
    print(f"Title: {title}")
    print(f"Transcript Length: {len(full_transcript)} characters")
    print(f"File saved to: ./exports/ai_context_ready.txt")

if __name__ == "__main__":
    url = ['NKnZYvZA7w4']
    prepare_for_ai(url)
```