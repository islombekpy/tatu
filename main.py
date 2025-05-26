# import json

# with open('salom.txt', 'r', encoding='utf-8') as file:
#     text = file.read()

# questions = []
# current_question = None

# for line in text.split("\n"):
#     line = line.strip()
#     if line.startswith("++++"):
#         if current_question:
#             questions.append(current_question)
#         current_question = {"question": line[5:].strip(), "answer": ""}
#     elif line.startswith("==== #") and current_question:
#         current_question["answer"] = line[6:].strip()

# if current_question and current_question["question"] and current_question["answer"]:
#     questions.append(current_question)

# with open('questions.json', 'w', encoding='utf-8') as json_file:
#     json.dump(questions, json_file, ensure_ascii=False, indent=4)

# print("JSON file saved as questions.json")

# import json
# import re

# text = open('salom.txt','r')
# text = text.read()
# blocks = text.split("+++++")
# qa_pairs = []

# for block in blocks:
#     lines = [line.strip() for line in block.strip().split("====") if line.strip()]
#     if len(lines) < 2:
#         continue
#     savol = lines[0].replace('\n', ' ').strip()
#     for line in lines[1:]:
#         if line.startswith("#"):
#             javob = line[1:].strip()
#             qa_pairs.append({
#                 "question": savol,
#                 "answer": javob
#             })
#             break
# json_data = json.dumps(qa_pairs, ensure_ascii=False, indent=4)
# print(json_data)

# # Agar faylga yozmoqchi bo'lsangiz:
# with open("savol_javoblar.json", "w", encoding="utf-8") as f:
#     f.write(json_data)

# import json

# # Fayldan matnni o‘qish
# with open('salom.txt', 'r', encoding='utf-8') as file:
#     text = file.read()

# # Bloklarni ajratish
# blocks = text.split("++++")

# qa_pairs = []

# for block in blocks:
#     lines = [line.strip() for line in block.strip().split("====") if line.strip()]
#     if len(lines) < 2:
#         continue
#     savol = lines[0].replace('\n', ' ').strip()
#     for line in lines[1:]:
#         if line.startswith("#"):
#             javob = line[1:].strip()
#             qa_pairs.append({
#                 "question": savol,
#                 "answer": javob
#             })
#             break

# # JSON faylga yozish
# with open("savol_javoblar.json", "w", encoding="utf-8") as f:
#     json.dump(qa_pairs, f, ensure_ascii=False, indent=4)

# print("✅ Barcha savol-javoblar JSON faylga yozildi.")
import json

def parse_questions(file_path):
    result = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    question = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('?'):
            question = line[1:].strip()
        elif line.startswith('+') and question:
            answer = line[1:].strip()
            result.append({
                "question": question,
                "answer": answer
            })
            question = None  # reset for next
    return result

# Fayl yo'lini shu yerga yozing
file_path = "salom.txt"
questions = parse_questions(file_path)

# Natijani JSON faylga yozish
with open("savollar.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=4)

print("Tayyor JSON fayl: savollar.json")
