import time
from pymongo import MongoClient
import json

# חיבור ל-MongoDB עם MONGO_URI שסיפקת
mongo_uri = "mongodb+srv://guedalia:guedalia050504@cluster.eenou.mongodb.net/?retryWrites=true&w=majority&appName=Clusters"
client = MongoClient(mongo_uri)

# בחירת מסד הנתונים והתיקייה
db = client['chat_db']
collection = db['chats']

# פונקציה לשמירת מסמכים לקובץ JSONL ולעדכון feedback ל-null
def save_feedback_to_file_and_update(feedback_type, output_file):
    documents = collection.find({"feedback": feedback_type})
    new_data_count = 0

    with open(output_file, 'a', encoding='utf-8') as file:
        for doc in documents:
            output_data = {
                "messages": doc.get("messages", [])
            }
            file.write(json.dumps(output_data, ensure_ascii=False) + '\n')
            new_data_count += 1
            collection.update_one({"_id": doc["_id"]}, {"$set": {"feedback": None}})

    if new_data_count > 0:
        print(f"{new_data_count} new records added to {output_file} and feedback set to null.")
    else:
        print(f"No new records to add for feedback '{feedback_type}'.")

# פונקציה שמבצעת את הפעולה כל 5 שניות
def collect_feedback_every_5_seconds():
    while True:
        print("Collecting feedback...")
        save_feedback_to_file_and_update("like", "liked_chats.jsonl")
        save_feedback_to_file_and_update("unlike", "unliked_chats.jsonl")
        time.sleep(5)  # המתנה של 5 שניות

# הפעלת האיסוף
collect_feedback_every_5_seconds()
