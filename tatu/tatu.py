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
        self.questions: Dict[str, Dict[str, Any]] = {}
        self.question_file_path = os.path.join(settings.BASE_DIR, "json/questions.json")
        self._load_questions()

    def _load_questions(self) -> None:
        try:
            with open(self.question_file_path, "r", encoding="utf-8") as file:
                question_data = json.load(file)
                
                # Validate JSON structure
                if not isinstance(question_data, list):
                    raise ValueError("Invalid JSON structure: Expected array of questions")
                
                for idx, q in enumerate(question_data):
                    if not isinstance(q, dict):
                        logger.warning(f"Skipping invalid question entry at index {idx}")
                        continue
                        
                    if "question" not in q or "answer" not in q:
                        logger.warning(f"Skipping incomplete question entry at index {idx}")
                        continue
                        
                    normalized_question = self._normalize(q["question"])
                    self.questions[normalized_question] = {
                        "answer": q["answer"],
                        "index": idx + 1  # 1-based index
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

    def get_answer(self, question: str) -> Optional[Dict[str, Any]]:
        if not question:
            return None
            
        question = self._normalize(question)
        return self.questions.get(question)

    def find_closest_match(self, question: str) -> Optional[Dict[str, Any]]:
        normalized = self._normalize(question)
        if not normalized:
            return None
    
        if normalized in self.questions:
            return self.questions[normalized]
            
        # Try partial matches
        for key, answer_data in self.questions.items():
            if normalized in key or key in normalized:
                return answer_data
                
        return None

    def get_answers_for_questions(self, questions_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        responses = []
        
        for item in questions_data:
            if not isinstance(item, dict):
                continue
                
            question_text = item.get("question", "")
            if not question_text:
                continue
                
            answer_data = self.get_answer(question_text)
            if not answer_data:
                answer_data = self.find_closest_match(question_text)
                
            responses.append({
                "question": question_text,
                "answer": answer_data.get("answer", "-") if answer_data else "-",
                "index": answer_data.get("index") if answer_data else None
            })
            
        return responses

# Initialize question manager only if not in migration
if not os.environ.get('RUN_MAIN') and not os.environ.get('RUNNING_MIGRATION'):
    try:
        question_manager = QuestionManager()
    except Exception as e:
        logger.error(f"Failed to initialize QuestionManager: {str(e)}")
        question_manager = None

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def search_answer(request) -> JsonResponse:
    response = JsonResponse({})
    response = _add_cors_headers(response)
    
    if request.method == "OPTIONS":
        return response
        
    if not question_manager:
        response = JsonResponse({"error": "Question service unavailable"}, status=503)
        return _add_cors_headers(response)
        
    try:
        data = json.loads(request.body.decode("utf-8"))
        if not isinstance(data, list):
            logger.warning("Invalid input format: not an array")
            response = JsonResponse({"error": "Input must be an array"}, status=400)
            return _add_cors_headers(response)

        responses = question_manager.get_answers_for_questions(data)
        response = JsonResponse(responses, safe=False)
        return _add_cors_headers(response)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        response = JsonResponse({"error": "Invalid JSON format"}, status=400)
        return _add_cors_headers(response)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        response = JsonResponse({"error": f"Server error: {str(e)}"}, status=500)
        return _add_cors_headers(response)

def _add_cors_headers(response):
    response["Access-Control-Allow-Origin"] = "https://student.fstu.uz"
    response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Accept"
    response["Access-Control-Allow-Credentials"] = "true"
    return response