import json

with open('quiz.txt', 'r', encoding='utf-8') as file:
    text = file.read()

questions = []
current_question = None

for line in text.split("\n"):
    line = line.strip()
    if line.startswith("++++"):
        if current_question:
            questions.append(current_question)
        current_question = {"question": line[5:].strip(), "answer": ""}
    elif line.startswith("==== #") and current_question:
        current_question["answer"] = line[6:].strip()

if current_question and current_question["question"] and current_question["answer"]:
    questions.append(current_question)

with open('questions.json', 'w', encoding='utf-8') as json_file:
    json.dump(questions, json_file, ensure_ascii=False, indent=4)

print("JSON file saved as questions.json")