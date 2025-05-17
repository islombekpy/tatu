import json
import os
import re
from typing import List, Dict, Any, Optional
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("question_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class QuestionManager:
    def __init__(self):
        self.questions: Dict[str, str] = {}
        self.question_file_path = os.path.join(settings.BASE_DIR, "json/questions.json")
        self._load_questions()

    def _load_questions(self) -> None:
        try:
            with open(self.question_file_path, "r", encoding="utf-8") as file:
                question_data = json.load(file)
                self.questions = {
                    self._normalize(q["question"]): q["answer"]  
                    for q in question_data
                }
            logger.info(f"Loaded {len(self.questions)} questions successfully")
        except FileNotFoundError:
            logger.error(f"JSON file not found: {self.question_file_path}")
            raise FileNotFoundError(f"JSON file not found: {self.question_file_path}")
        except json.JSONDecodeError:
            logger.error("Invalid JSON file format!")
            raise ValueError("Invalid JSON file format")

    def _normalize(self, text: str) -> str:
        if not text or not isinstance(text, str):
            return ""
        
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)  
        text = re.sub(r"[^\w\s]", "", text)  
        return text

    def get_answer(self, question: str) -> Optional[str]:
        if not question:
            return None
            
        question = self._normalize(question)
        return self.questions.get(question)

    def find_closest_match(self, question: str) -> Optional[str]:
        normalized = self._normalize(question)
        if not normalized:
            return None
    
        if normalized in self.questions:
            return self.questions[normalized]
        for key, answer in self.questions.items():
            if normalized in key or key in normalized:
                return answer
                
        return None

    def get_answers_for_questions(self, questions_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        responses = []
        
        for item in questions_data:
            question_text = item.get("question", "")
            if not question_text:
                continue
                
            normalized_question = self._normalize(question_text)
            answer = self.get_answer(normalized_question)
            if not answer:
                answer = self.find_closest_match(question_text)
                
            final_answer = answer or "-"
            logger.info(f"Question: {question_text}")
            logger.info(f"Normalized: {normalized_question}")
            logger.info(f"Answer: {final_answer}")
            responses.append({
                "question": question_text,
                "answer": final_answer
            })
            
        return responses

question_manager = QuestionManager()

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def search_answer(request) -> JsonResponse:
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response = _add_cors_headers(response)
        return response
        
    try:
        data = json.loads(request.body.decode("utf-8"))
        if not isinstance(data, list):
            logger.warning("Invalid input format: not an array")
            return JsonResponse({"error": "Input must be an array"}, status=400)

        responses = question_manager.get_answers_for_questions(data)
        response = JsonResponse(responses, safe=False)
        response = _add_cors_headers(response)
        
        return response
    except json.JSONDecodeError:
        logger.error("JSON parsing error")
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return JsonResponse({"error": f"Error: {str(e)}"}, status=500)

def _add_cors_headers(response):
    """Add CORS headers to response."""
    response["Access-Control-Allow-Origin"] = "https://student.fstu.uz"
    response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Accept"
    return response