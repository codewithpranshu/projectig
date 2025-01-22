# Scripted by Zork ! 


import telebot
from telebot import types
import instaloader
import os
import time

t = telebot.TeleBot("7874122831:AAGOp2qDFrqupPocwoS3klc9rR7LMTxfH2s")

user_state = {}
user_message_ids = {}
start_over_message_ids = {}
success_message_ids = {}

@t.message_handler(commands=['start'])
def question(message):
    welcome_text = (
        "✅ Welcome to the Highest Quality FREE Instagram Downloader bot for OFM!\n\n"
        "⚡ Key Features:\n"
        "- Download Instagram videos without watermarks\n"
        "- Removed metadata for extra privacy\n"
        "- Download Instagram Reels / Posts / Stories\n"
        "⬇️ Select from the options below:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📹 Download Instagram Reels", callback_data="download_reel"),
        types.InlineKeyboardButton("🖼 Download Profile Photo", callback_data="profile_photo_download"),
        types.InlineKeyboardButton("📱 Download Story", callback_data="download_story"),
        types.InlineKeyboardButton("📊 Scrape Instagram Profile", callback_data="scrape_profile")
    )
    t.send_message(message.chat.id, welcome_text, reply_markup=markup)

def send_welcome_message(chat_id):
    welcome_text = (
        "✅ Welcome to the Highest Quality FREE Instagram Downloader bot for OFM!\n\n"
        "⚡ Key Features:\n"
        "- Download Instagram videos without watermarks\n"
        "- Removed metadata for extra privacy\n"
        "- Download Instagram Reels / Posts / Stories\n"
        "⬇️ Select from the options below:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📹 Download Instagram Reels", callback_data="download_reel"),
        types.InlineKeyboardButton("🖼 Download Profile Photo", callback_data="profile_photo_download"),
        types.InlineKeyboardButton("📱 Download Story", callback_data="download_story"),
        types.InlineKeyboardButton("📊 Scrape Instagram Profile", callback_data="scrape_profile")
    )
    t.send_message(chat_id, welcome_text, reply_markup=markup)

@t.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "profile_photo_download":
        msg = t.send_message(call.message.chat.id, "Enter the Instagram Username:")
        user_state[call.message.chat.id] = "awaiting_username"
        user_message_ids[call.message.chat.id] = msg.message_id
        
    elif call.data == "download_reel":
        msg = t.send_message(call.message.chat.id, "Enter the Instagram Reel Link:")
        user_state[call.message.chat.id] = "awaiting_reel_url"
        user_message_ids[call.message.chat.id] = msg.message_id
        
    elif call.data == "start_over":
        chat_id = call.message.chat.id
        

        if chat_id in start_over_message_ids:
            try:
                t.delete_message(chat_id, start_over_message_ids[chat_id])
            except:
                pass
            start_over_message_ids.pop(chat_id, None)
        

        if chat_id in success_message_ids:
            try:
                t.delete_message(chat_id, success_message_ids[chat_id])
            except:
                pass
            success_message_ids.pop(chat_id, None)
        

        send_welcome_message(chat_id)

        t.answer_callback_query(call.id)
        
        
@t.message_handler(func=lambda message: user_state.get(message.chat.id) == "awaiting_reel_url")
def handle_reel_url_input(message):
    if message.chat.id in user_message_ids:
        t.delete_message(message.chat.id, user_message_ids[message.chat.id])
        user_message_ids.pop(message.chat.id, None)
    
    # Send "Processing" message
    processing_msg = t.send_message(message.chat.id, "⏳ Processing ...")
    animation_frames = ["⏳ Processing .", "⏳ Processing ..", "⏳ Processing ..."]
    
    for _ in range(3):
        for frame in animation_frames:
            t.edit_message_text(frame, message.chat.id, processing_msg.message_id)
            time.sleep(0.5)
    
    try:
        # Initialize Instaloader instance for downloading Reels
        loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern='',
            max_connection_attempts=0,
            quiet=True  
        )

     
        url = message.text.strip()  
        if not url:
            t.delete_message(message.chat.id, processing_msg.message_id)
            t.send_message(message.chat.id, "❌ No URL provided.")
            return

        shortcode = url.split("/")[-2]  

      
        if not shortcode:
            t.delete_message(message.chat.id, processing_msg.message_id)
            t.send_message(message.chat.id, "❌ Invalid URL format.")
            return

        print(f"Attempting to download Reel with shortcode: {shortcode}")  
        
    
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        

        target_directory = str(message.chat.id)  
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)  
        
        video_file_path = os.path.join(target_directory, f"{shortcode}.mp4")

  
        print(f"Target directory: {target_directory}")
        
      
        loader.download_post(post, target=target_directory)

     
        downloaded_files = os.listdir(target_directory)
        video_file = None
        for file in downloaded_files:
            if file.endswith(".mp4"):  
                video_file = file
                break

        if video_file:

            video_file_path = os.path.join(target_directory, video_file)

            print(f"Video file found at: {video_file_path}")  
            
     
            renamed_video_path = os.path.join(target_directory, f"{shortcode}_{time.strftime('%Y-%m-%d_%H-%M-%S_UTC')}.mp4")
            os.rename(video_file_path, renamed_video_path) 

         
            caption = post.caption or "No caption provided."

        
            with open(renamed_video_path, 'rb') as video:
                t.send_video(
                    message.chat.id,
                    video,
                    caption=f"{caption}",
                    disable_notification=True
                )
            
          
            t.delete_message(message.chat.id, processing_msg.message_id)
            
          
            start_over_markup = types.InlineKeyboardMarkup(row_width=1)
            start_over_markup.add(types.InlineKeyboardButton("Click here", callback_data="start_over"))
            start_over_msg = t.send_message(message.chat.id, "🔄 Want to start over?", reply_markup=start_over_markup)
            start_over_message_ids[message.chat.id] = start_over_msg.message_id
            
        
            if os.path.exists(target_directory):
                for file_name in os.listdir(target_directory):
                    os.remove(os.path.join(target_directory, file_name))  
                os.rmdir(target_directory) 

        else:
            
            print(f"Video file not found in target directory: {target_directory}")
            t.delete_message(message.chat.id, processing_msg.message_id)
            t.send_message(message.chat.id, "❌ The video was not downloaded properly.")
    
    except Exception as e:
        t.delete_message(message.chat.id, processing_msg.message_id)
        print(f"Error while downloading Reel: {str(e)}")  
        t.send_message(message.chat.id, f"❌ An error occurred: {str(e)}")
    
    user_state.pop(message.chat.id, None)




@t.message_handler(func=lambda message: user_state.get(message.chat.id) == "awaiting_username")
def handle_username_input(message):
    if message.chat.id in user_message_ids:
        t.delete_message(message.chat.id, user_message_ids[message.chat.id])
        user_message_ids.pop(message.chat.id, None)
    

    processing_msg = t.send_message(message.chat.id, "⏳ Processing ...")
    animation_frames = ["⏳ Processing .", "⏳ Processing ..", "⏳ Processing ..."]
    
    for _ in range(3):
        for frame in animation_frames:
            t.edit_message_text(frame, message.chat.id, processing_msg.message_id)
            time.sleep(0.5)
    
    try:
        loader = instaloader.Instaloader(
            download_pictures=True,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern='',
            max_connection_attempts=0
        )

        profile = loader.check_profile_id(message.text)
        loader.download_profilepic(profile)

        folder_name = message.text
        photo_path = None
        if os.path.exists(folder_name):
            for file_name in os.listdir(folder_name):
                if file_name.endswith(".jpg"):
                    photo_path = os.path.join(folder_name, file_name)
                    break

        if photo_path:
            with open(photo_path, "rb") as photo:
                t.send_photo(
                    message.chat.id,
                    photo,
                    protect_content=False,  
                    disable_notification=True,  
                    allow_sending_without_reply=True
                )
            
            t.delete_message(message.chat.id, processing_msg.message_id)
            
            success_msg = t.send_message(message.chat.id, "✅ Profile photo downloaded successfully!")
            success_message_ids[message.chat.id] = success_msg.message_id
        
            start_over_markup = types.InlineKeyboardMarkup(row_width=1)
            start_over_markup.add(types.InlineKeyboardButton("Click here", callback_data="start_over"))
            start_over_msg = t.send_message(message.chat.id, "🔄 Want to start over?", reply_markup=start_over_markup)
            start_over_message_ids[message.chat.id] = start_over_msg.message_id
        else:
            t.delete_message(message.chat.id, processing_msg.message_id)
            t.send_message(message.chat.id, "❌ Profile photo not found.")
        
        if os.path.exists(folder_name):
            for file_name in os.listdir(folder_name):
                os.remove(os.path.join(folder_name, file_name))
            os.rmdir(folder_name)
    except Exception as e:
        t.delete_message(message.chat.id, processing_msg.message_id)
        t.send_message(message.chat.id, f"❌ An error occurred: {str(e)}")
    
    user_state.pop(message.chat.id, None)


t.polling()

