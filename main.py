import os
import sys
import telebot
import urllib.request
import json
from groq import Groq

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

if not BOT_TOKEN or not GROQ_KEY:
    print("[!] Error: Environment variables missing.")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

def process_with_groq(text_input):
    client = Groq(api_key=GROQ_KEY)
    prompt = f"""
    Context: You are the 'Ci' Coordinator. Analyze chaos and provide short, cold, value-driven 1-on-1 control cards for US owners. No platforms, no invented prices. 
    Format:
    [THE MESS]
    - Bullet points of what is broken.
    [THE CONTROL CARD]
    - Fact: (1 sentence)
    - State: (Current position)
    - Risk: (What happens if ignored)
    - Action: (Immediate tactical human step)
    [THE NEXT STEP]
    "Send me your next mess. I will turn it into a control card for free. If it brings clarity, we talk about automation. Reply to lock this coordinate."
    Input: {text_input}
    Output Language: English (US)
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.0
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Groq Error: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "⚙️ [Ci Cloud Core Active]\n\nБот працює автономно в хмарі. Команда /flux — видобуток лідів з США.")

@bot.message_handler(commands=['flux'])
def mine_leads(message):
    bot.send_message(message.chat.id, "🔎 Connecting to US Data Flow...")
    new_stories_url = "https://hacker-news.firebaseio.com/v0/newstories.json"
    
    try:
        req = urllib.request.Request(new_stories_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            story_ids = json.loads(response.read().decode())[:5]
            
        count = 0
        for s_id in story_ids:
            if count >= 3: break
            item_url = f"https://hacker-news.firebaseio.com/v0/item/{s_id}.json"
            req_item = urllib.request.Request(item_url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req_item) as item_resp:
                story = json.loads(item_resp.read().decode())
                if not story or 'title' not in story: continue
                
                title = story.get('title', '')
                text = story.get('text', 'No extended text.')
                url = story.get('url', f"https://news.ycombinator.com/item?id={s_id}")
                
                full_chaos = f"{title}. {text}"[:500]
                card = process_with_groq(full_chaos)
                
                response_text = f"🔥 **NEW USA LEAD FOUND**\n🔗 [Link to Thread]({url})\n\n{card}"
                bot.send_message(message.chat.id, response_text, parse_mode='Markdown', disable_web_page_preview=True)
                count += 1
                
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Mining Error: {str(e)}")

@bot.message_handler(func=lambda message: True)
def handle_text_chaos(message):
    card = process_with_groq(message.text)
    bot.reply_to(message, card)

if __name__ == "__main__":
    print("[+] Cloud Bot is pooling...")
    bot.infinity_polling()
