import requests
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionType(Enum):
    MCQ = "mcq"
    FILLUP = "fillup"
    CODING = "coding"


class QuestionGenerator:
    """Generate quiz questions using Mistral 7B via Ollama - FIXED VERSION"""

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """Initialize the question generator"""
        self.ollama_url = ollama_url
        self.model = "gemma3:4b"
        self.temperature = 0.3  # FIXED: Lowered from 0.7 for consistent JSON output
        self.test_connection()

    def test_connection(self) -> bool:
        """Test if Ollama server is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Connected to Ollama server")
                print(f"✅ Model '{self.model}' is available")
                return True
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Ollama server")
            print("   Start with: ollama serve")
            raise

    def generate_mcq(self, topic: str, difficulty: str = "easy", count: int = 3) -> tuple:
        """Generate MCQ questions - FIXED"""

        prompt = f"""You are an expert exam question designer.

TASK:
Generate exactly {count} MULTIPLE CHOICE QUESTIONS on the topic "{topic}" with difficulty "{difficulty}".

CRITICAL OUTPUT RULES (NON-NEGOTIABLE):
1. Output MUST be a valid JSON ARRAY only.
2. Do NOT include markdown, comments, explanations outside JSON, or extra text.
3. The JSON must be parsable using json.loads() without modification.
4. Follow the JSON schema EXACTLY as shown below. Do NOT add or remove fields.
5. Every question MUST strictly match the requested difficulty.

DIFFICULTY CALIBRATION (VERY STRICT):
- EASY:
  - Direct fact or definition
  - Single concept
  - One option is clearly correct
  - No tricks, no close options

- MEDIUM:
  - Conceptual understanding required
  - Small scenario or application-based
  - 1 correct option, 1 distractor that seems plausible
  - Requires short reasoning

- HARD:
  - Requires deep reasoning or elimination
  - At least TWO options must look correct at first glance
  - Focus on edge cases, subtle differences, or hidden constraints
  - NOT factual recall

QUALITY RULES:
- Questions must be technically accurate
- Options must be non-trivial and well differentiated
- Do NOT repeat the same question pattern
- Avoid vague or subjective wording

JSON SCHEMA (COPY EXACTLY):
[
  {{
    "id": 1,
    "topic": "{topic}",
    "difficulty": "{difficulty}",
    "type": "mcq",
    "question": "Clear and precise question text",
    "options": {{
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D"
    }},
    "correct_answer": "A",
    "explanation": "Short technical explanation justifying why this option is correct"
  }}
]

FINAL REMINDER:
Return ONLY the JSON array.
Generate exactly {count} questions.
"""

        print(f"\n🔄 Generating {count} MCQ questions...")
        print(f"   Topic: {topic}, Difficulty: {difficulty}")
        start_time = time.time()
        raw_output = self._call_ollama(prompt)
        elapsed = time.time() - start_time

        questions = self._parse_mcq(raw_output, topic, difficulty, count)

        print(f"✅ Generated {len(questions)} questions in {elapsed:.2f}s")
        return questions, elapsed

    def generate_fillup(self, topic: str, difficulty: str = "easy", count: int = 3) -> tuple:
        """Generate fill-in-the-blank questions - FIXED"""

        prompt =f"""You are an expert academic question designer.

TASK:
Generate exactly {count} FILL-IN-THE-BLANK questions on the topic "{topic}" with difficulty "{difficulty}".

CRITICAL "ANTI-REPETITION" RULES:
1. EACH question must test a COMPLETELY DIFFERENT concept.
2. The "correct_word" MUST be different for every question.
3. If Question 1 answer is "Voltage", Question 2 CANNOT be "Voltage".
4. Do NOT use the same sentence structure repeatedly.

DIFFICULTY CALIBRATION:
- EASY: Direct definition. (e.g., "The basic unit of life is the ___.")
- MEDIUM: Application of a concept.
- HARD: Edge cases, specific conditions, or relationships between concepts.

JSON SCHEMA (Strictly follow this):
[
  {{
    "id": 1,
    "topic": "{topic}",
    "difficulty": "{difficulty}",
    "type": "fillup",
    "question": "Sentence with ___ as the blank",
    "correct_word": "ExactCorrectAnswer",
    "hint": "Short hint",
    "explanation": "Why this word fits"
  }}
]

EXAMPLE (For structure only):
[
  {{
    "id": 1,
    "question": "In Python, the ___ keyword is used to define a function.",
    "correct_word": "def"
  }},
  {{
    "id": 2,
    "question": "An unchangeable list in Python is called a ___.",
    "correct_word": "tuple"
  }}
]

FINAL INSTRUCTION:
Generate exactly {count} unique questions. Return ONLY the JSON array.
"""

        print(f"\n🔄 Generating {count} Fill-up questions...")
        print(f"   Topic: {topic}, Difficulty: {difficulty}")

        start_time = time.time()
        raw_output = self._call_ollama(prompt)
        elapsed = time.time() - start_time

        questions = self._parse_fillup(raw_output, topic, difficulty, count)

        print(f"✅ Generated {len(questions)} questions in {elapsed:.2f}s")
        return questions, elapsed

    def generate_coding(self, topic: str, difficulty: str = "easy", count: int = 3) -> tuple:
        """Generate coding challenge questions"""

        prompt = f"""You are an expert programming question setter for technical interviews and exams.

    TASK:
    Generate {count} CODING questions for the topic "{topic}" with difficulty "{difficulty}".

    IMPORTANT RULES:
    1. The topic will ALWAYS be a coding-related domain (e.g., Python, Java, DSA, Spring Boot, TensorFlow, Hive, Semaphores).
    2. Do NOT generate purely theoretical questions.
    3. Difficulty must be increased by LOGIC, EDGE CASES, or CONSTRAINTS — NOT by long code.
    4. Avoid full-scale applications or very long programs.
       - For Spring Boot: ask for specific files only (Controller, Service, Repository).
       - For Hive/SQL: advanced queries are allowed.
       - For DSA: focus on time/space complexity and edge cases.
    5. Questions must be solvable within reasonable code length.

    DIFFICULTY GUIDELINES:
    - Easy: Basic logic, single concept
    - Medium: Multiple conditions, efficiency matters
    - Hard: Tricky logic, constraints-driven thinking (NOT long code)

    OUTPUT FORMAT:
    Return ONLY a valid JSON array.
    NO markdown, NO explanations, NO comments.

    Each JSON object MUST have EXACTLY these fields:

    [
      {{
        "id": 1,
        "topic": "{topic}",
        "difficulty": "{difficulty}",
        "type": "coding",
        "question": "Problem statement describing what to implement",
        "input": "Description of input format",
        "output": "Description of output format",
        "constraints": "Important constraints and edge cases",
        "expected_output_example": "Expected output for a sample input"
      }}
    ]

    FINAL REMINDERS:
    - Keep questions practical and implementation-focused
    - Difficulty comes from logic, not code length
    - Output MUST be strict JSON

    Now generate {count} coding questions.
    """

        print(f"\n🔄 Generating {count} Coding questions...")
        print(f"   Topic: {topic}, Difficulty: {difficulty}")

        start_time = time.time()
        raw_output = self._call_ollama(prompt)
        elapsed = time.time() - start_time

        questions = self._parse_coding(raw_output, topic, difficulty, count)

        print(f"✅ Generated {len(questions)} questions in {elapsed:.2f}s")
        return questions, elapsed

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API and get response"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": self.temperature,
                    "top_p": 0.9,  # Added for more consistent outputs
                    "top_k": 40,  # Added for better quality
                },
                # timeout=120
            )

            if response.status_code != 200:
                print(f"❌ Ollama error: {response.status_code}")
                raise Exception(f"Ollama returned {response.status_code}")

            return response.json().get("response", "")

        except requests.exceptions.Timeout:
            print("❌ Timeout - model taking too long")
            raise
        except Exception as e:
            print(f"❌ Error: {e}")
            raise

    def _extract_json(self, raw_output: str) -> str:
        """Extract JSON from various formats - ROBUST"""
        # Remove markdown code blocks
        raw_output = re.sub(r'```json\s*', '', raw_output)
        raw_output = re.sub(r'```\s*', '', raw_output)

        # Try to find JSON array or object
        json_match = re.search(r'(\[.*\]|\{.*\})', raw_output, re.DOTALL)
        if json_match:
            return json_match.group(1)

        return raw_output.strip()

    def _parse_mcq(self, raw_output: str, topic: str, difficulty: str, count: int) -> List[Dict]:
        """Parse MCQ JSON format - ROBUST with fallback"""

        # Extract JSON
        cleaned = self._extract_json(raw_output)

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                # Validate and fix each question
                valid_questions = []
                for i, q in enumerate(parsed, 1):
                    if isinstance(q, dict):
                        # Ensure required fields
                        validated = {
                            "id": q.get("id", i),
                            "topic": q.get("topic", topic),
                            "difficulty": q.get("difficulty", difficulty),
                            "type": "mcq",
                            "question": q.get("question", ""),
                            "options": q.get("options", {}),
                            "correct_answer": q.get("correct_answer", "A"),
                            "explanation": q.get("explanation", "")
                        }
                        # Only add if has question and options
                        if validated["question"] and validated["options"]:
                            valid_questions.append(validated)

                if valid_questions:
                    return valid_questions

            elif isinstance(parsed, dict):
                # Single question
                validated = {
                    "id": parsed.get("id", 1),
                    "topic": parsed.get("topic", topic),
                    "difficulty": parsed.get("difficulty", difficulty),
                    "type": "mcq",
                    "question": parsed.get("question", ""),
                    "options": parsed.get("options", {}),
                    "correct_answer": parsed.get("correct_answer", "A"),
                    "explanation": parsed.get("explanation", "")
                }
                if validated["question"] and validated["options"]:
                    return [validated]

        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parse failed: {e}")
            print(f"⚠️  Raw output: {raw_output[:200]}...")

        # Fallback: Generate basic questions
        print("⚠️  Using fallback generation")
        return self._generate_fallback_mcq(topic, difficulty, count)

    def _parse_fillup(self, raw_output: str, topic: str, difficulty: str, count: int) -> List[Dict]:
        """Parse fill-up JSON format - ROBUST with fallback"""

        cleaned = self._extract_json(raw_output)

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                valid_questions = []
                for i, q in enumerate(parsed, 1):
                    if isinstance(q, dict):
                        validated = {
                            "id": q.get("id", i),
                            "topic": q.get("topic", topic),
                            "difficulty": q.get("difficulty", difficulty),
                            "type": "fillup",
                            "question": q.get("question", ""),
                            "correct_word": q.get("correct_word", ""),
                            "hint": q.get("hint", ""),
                            "explanation": q.get("explanation", "")
                        }
                        if validated["question"] and validated["correct_word"]:
                            valid_questions.append(validated)

                if valid_questions:
                    return valid_questions

            elif isinstance(parsed, dict):
                validated = {
                    "id": parsed.get("id", 1),
                    "topic": parsed.get("topic", topic),
                    "difficulty": parsed.get("difficulty", difficulty),
                    "type": "fillup",
                    "question": parsed.get("question", ""),
                    "correct_word": parsed.get("correct_word", ""),
                    "hint": parsed.get("hint", ""),
                    "explanation": parsed.get("explanation", "")
                }
                if validated["question"] and validated["correct_word"]:
                    return [validated]

        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parse failed: {e}")

        print("⚠️  Using fallback generation")
        return self._generate_fallback_fillup(topic, difficulty, count)

    def _parse_coding(self, raw_output: str, topic: str, difficulty: str, count: int) -> List[Dict]:
        """Parse Coding JSON format - ROBUST, SCHEMA-ALIGNED"""

        cleaned = self._extract_json(raw_output)

        try:
            parsed = json.loads(cleaned)

            if isinstance(parsed, dict):
                parsed = [parsed]  # normalize single object to list

            if not isinstance(parsed, list):
                raise ValueError("Parsed JSON is not a list")

            valid_questions = []

            for i, q in enumerate(parsed, start=1):
                if not isinstance(q, dict):
                    continue

                validated = {
                    "id": q.get("id", i),
                    "topic": q.get("topic", topic),
                    "difficulty": q.get("difficulty", difficulty),
                    "type": "coding",
                    "question": q.get("question", "").strip(),
                    "input": q.get("input", "").strip(),
                    "output": q.get("output", "").strip(),
                    "constraints": q.get("constraints", "").strip(),
                    "expected_output_example": q.get("expected_output_example", "").strip(),
                    "time_limit_seconds": q.get("time_limit_seconds", 120),
                }

                # Minimal validation (DO NOT over-restrict)
                if validated["question"] and validated["input"] and validated["output"]:
                    valid_questions.append(validated)

            if valid_questions:
                return valid_questions[:count]

        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ Coding JSON parse failed: {e}")

        print("⚠️ Using fallback generation for coding questions")
        return self._generate_fallback_coding(topic, difficulty, count)

    def _generate_fallback_mcq(self, topic: str, difficulty: str, count: int) -> List[Dict]:
        """Generate basic MCQ questions when model fails"""
        return [{
            "id": i + 1,
            "topic": topic,
            "difficulty": difficulty,
            "type": "mcq",
            "question": f"What is an important concept in {topic}? (Question {i + 1})",
            "options": {
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            },
            "correct_answer": "A",
            "explanation": "This is a fallback question. Please regenerate for better quality."
        } for i in range(count)]

    def _generate_fallback_fillup(self, topic: str, difficulty: str, count: int) -> List[Dict]:
        """Generate basic fill-up questions when model fails"""
        return [{
            "id": i + 1,
            "topic": topic,
            "difficulty": difficulty,
            "type": "fillup",
            "question": f"In {topic}, ___ is an important concept (Question {i + 1})",
            "correct_word": "placeholder",
            "hint": "Key concept",
            "explanation": "This is a fallback question. Please regenerate for better quality."
        } for i in range(count)]

    def _generate_fallback_coding(self, topic: str, difficulty: str, count: int) -> List[Dict]:
        """Generate basic coding questions when model fails"""
        time_limits = {"easy": 120, "medium": 180, "hard": 300}
        return [{
            "id": i + 1,
            "topic": topic,
            "difficulty": difficulty,
            "type": "coding",
            "question": f"Write a function for {topic} (Question {i + 1})",
            "function_name": f"solve_{i + 1}",
            "test_input": "input",
            "expected_output": "output",
            "time_limit_seconds": time_limits.get(difficulty, 120)
        } for i in range(count)]


# Test if working
if __name__ == "__main__":
    gen = QuestionGenerator()

    # Test MCQ
    print("\n" + "=" * 60)
    print("Testing MCQ Generation")
    print("=" * 60)
    questions, elapsed = gen.generate_mcq("Spring Boot", "hard", 2)
    print(json.dumps(questions, indent=2))

    # Test Fill-up
    print("\n" + "=" * 60)
    print("Testing Fill-up Generation")
    print("=" * 60)
    questions, elapsed = gen.generate_fillup("SQL", "medium", 2)
    print(json.dumps(questions, indent=2))

    # Test Coding
    print("\n" + "=" * 60)
    print("Testing Coding Generation")
    print("=" * 60)
    questions, elapsed = gen.generate_coding("Node js", "easy", 2)
    print(json.dumps(questions, indent=2))