import json
from fpdf import FPDF
import os

# תיקיית הקבצים שנוצרו על ידי קוד 1
input_folder = r"C:\\Users\\neria\\PycharmProjects\\MONGO_TO_JSON"

# פונקציה לטעינת קובצי JSONL מקוד 1
def load_jsonl_files(folder):
    all_data = {"like": [], "unlike": []}
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path) and filename.endswith('.jsonl'):
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()  # הסרת רווחים מיותרים
                    if not line:  # דילוג על שורות ריקות
                        continue
                    try:
                        data = json.loads(line)  # קריאה של כל שורה כ-JSON
                        # זיהוי מדויק של הקובץ לפי שמו
                        if filename == "liked_chats.jsonl":  # קובץ like
                            all_data["like"].append(data)
                        elif filename == "unliked_chats.jsonl":  # קובץ unlike
                            all_data["unlike"].append(data)
                    except json.JSONDecodeError as e:
                        print(f"Skipping invalid JSON line in file {filename}: {line}")
                        continue
    return all_data

# פונקציה למיזוג נתונים עם קובץ final
def merge_with_final(data, final_file):
    # אם אין נתונים חדשים, פשוט נחזיר
    if not data:
        print(f"No new data to merge into {final_file}.")
        return

    # אם הקובץ קיים, נטען את התוכן
    if os.path.exists(final_file):
        if os.stat(final_file).st_size == 0:
            existing_data = []  # קובץ ריק => רשימה ריקה
        else:
            with open(final_file, 'r', encoding='utf-8') as file:
                existing_data = json.load(file)
    else:
        existing_data = []

    # מיזוג הנתונים
    existing_data.extend(data)

    # כתיבה חזרה לקובץ
    with open(final_file, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)
    print(f"Merged data into {final_file}.")

# פונקציה לקריאת JSON סופי
def load_final_json(output_file):
    if os.path.exists(output_file):
        if os.stat(output_file).st_size == 0:  # בדיקה אם הקובץ ריק
            return []
        with open(output_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

# פונקציה ליצירת PDF בצורה קריאה ונוחה
def create_readable_pdf(data, output_pdf, title):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # הוספת כותרת
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)

    # הוספת שיחות בפורמט קריא
    pdf.set_font("Arial", size=12)
    for idx, chat in enumerate(data, 1):
        pdf.cell(0, 10, f"Conversation {idx}:", ln=True)
        pdf.ln(2)
        for message in chat.get("messages", []):
            role = message.get("role", "unknown").capitalize()
            content = message.get("content", "")
            pdf.multi_cell(0, 10, f"{role}: {content}")
            pdf.ln(2)
        pdf.ln(5)

    pdf.output(output_pdf, "F")
    print(f"PDF created: {output_pdf}")

# פונקציה לריקון תוכן הקבצים
def clear_json_file_content(file_path):
    """מרוקן את התוכן של קובץ JSONL (משאיר אותו ריק)"""
    print(f"Clearing content of: {file_path}")
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('')  # השארת הקובץ ריק
    print(f"Content cleared for file: {file_path}")

# פונקציה לריקון כל קבצי ה-JSON בתיקייה
def clear_input_files(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path) and filename.endswith('.jsonl'):
            print(f"Clearing file: {file_path}")
            clear_json_file_content(file_path)

# קבצים ותיקיות
liked_pdf = "good_conversations.pdf"
unliked_pdf = "bad_conversations.pdf"
final_liked_json = "final_liked_chats.json"
final_unliked_json = "final_unliked_chats.json"

print("Merging new data into final files...")

# שלב 1: טעינת נתונים מקוד 1
new_data = load_jsonl_files(input_folder)

# שלב 2: מיזוג הנתונים לקבצי final
merge_with_final(new_data["like"], final_liked_json)
merge_with_final(new_data["unlike"], final_unliked_json)

# שלב 3: יצירת PDF
print("Generating new PDFs based on final data files...")

# קריאת נתוני final_liked ויצירת PDF קריא
liked_data = load_final_json(final_liked_json)
if liked_data:
    create_readable_pdf(liked_data, liked_pdf, "Good Conversations")
else:
    print("No data found for liked chats.")

# קריאת נתוני final_unliked ויצירת PDF קריא
unliked_data = load_final_json(final_unliked_json)
if unliked_data:
    create_readable_pdf(unliked_data, unliked_pdf, "Bad Conversations")
else:
    print("No data found for unliked chats.")

# שלב 4: ניקוי נתונים מקובצי JSON שנוצרו על ידי קוד 1
clear_input_files(input_folder)
