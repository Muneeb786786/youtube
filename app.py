from flask import Flask, request, jsonify
import yt_dlp
import pafy
import os

# Set Pafy to use internal backend as fallback
os.environ["PAFY_BACKEND"] = "internal"

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the Video API!"})

@app.route("/get_video", methods=["GET"])
def get_video():
    try:
        # Get URL from request
        url = request.args.get("url")
        
        if not url:
            return jsonify({"error": "No video URL provided"}), 400
        
        # Try using yt-dlp directly first (more reliable)
        try:
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = info['url']
                
                return jsonify({
                    "title": info.get('title', 'Unknown'),
                    "duration": str(info.get('duration', 'Unknown')),
                    "direct_url": video_url
                })
                
        # Fall back to pafy if yt-dlp direct approach fails
        except Exception as ydlp_error:
            try:
                video = pafy.new(url)
                best_stream = video.getbest()
                
                return jsonify({
                    "title": video.title,
                    "duration": video.duration,
                    "direct_url": best_stream.url
                })
            except Exception as pafy_error:
                return jsonify({"error": "Failed to fetch video details"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Required for Vercel serverless functions
def handler(event, context):
    return app(event, context)