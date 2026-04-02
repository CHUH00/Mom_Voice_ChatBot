import os
import logging
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from typing import List, Dict, Optional
import json
from dotenv import load_dotenv

load_dotenv("backend/.env")

logger = logging.getLogger(__name__)

class PersonaEngine:
    def __init__(self, model_name="llama-3.3-70b-versatile", api_key=None):
        self.model_name = model_name
        groq_api_key = api_key or os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            logger.error("GROQ_API_KEY is not set.")
        self.llm = ChatGroq(
            temperature=0.9,
            model_name=self.model_name,
            groq_api_key=groq_api_key
        ) if groq_api_key else None
        
    def extract_persona_rules(self, texts: List[str], user_notes: str) -> Dict:
        """
        Extract styling rules based on transcriptions and user manually provided memory notes.
        """
        combined_text = "\n".join(texts[:50]) # Use up to 50 transcript segments to extract style
        
        prompt = PromptTemplate(
            input_variables=["texts", "user_notes"],
            template="""
            당신은 화자 스타일 분석가입니다. 아래 제공된 발화(text)와 사용자의 메모(notes)를 바탕으로 엄마의 성격, 말투, 특징을 JSON 형태로 정리하십시오.
            
            발화 기록:
            {texts}
            
            사용자 메모:
            {user_notes}
            
            반드시 아래 키를 가진 JSON 포맷으로 대답하라:
            - tone: (예: "따뜻함", "무뚝뚝함")
            - common_phrases: ["자주 쓰는 말1", "자주 쓰는 말2"]
            - endings: ["~했어?", "~니?", "~다"]
            - topics: ["자주 언급하는 주제"]
            """
        )
        
        if not self.llm:
            logger.error("LLM is not initialized.")
            return {}

        # This assumes the LLM can output JSON correctly
        chain = prompt | self.llm
        try:
            response_obj = chain.invoke({"texts": combined_text, "user_notes": user_notes})
            response = str(getattr(response_obj, 'content', response_obj))
            
            # Naive parsing
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx != -1 and end_idx != -1:
                return json.loads(response[start_idx:end_idx])
            else:
                return {"error": "Failed to parse JSON", "raw": response}
        except Exception as e:
            logger.error(f"Failed to extract persona: {e}")
            return {}

    def chat_with_persona(self, query: str, profile_rules: Dict, chat_history: Optional[List[str]] = None):
        """
        Generate a response maintaining the persona.
        """
        rules_str = json.dumps(profile_rules, ensure_ascii=False)
        history_str = "\n".join(chat_history or [])
        
        FEW_SHOT_EXAMPLES = """
        [실제 대화 예시 - 이 말투와 분위기를 그대로 따라 하세요]
        자녀: 밥 먹었어?
        엄마: 응 먹었엉~ 막내는 뭐 먹엉?

        자녀: 집에 언제 들어가?
        엄마: 좀만 있으면 가~ 운전 조심해서 와.

        자녀: 시험 끝났어.
        엄마: 수고했어~ 맛있는 거 사먹어 울막내.

        자녀: 엄마 보고 싶어.
        엄마: 그랭~ 엄마도 막내 보고 싶었어.

        자녀: 저 지금 출발할게요.
        엄마: 오케이~ 조심해서 와 막내야.

        자녀: 오늘 좀 힘들었어.
        엄마: 왜~ 무슨 일 있었어? 얘기해봐.

        자녀: 요즘 잘 못 자고 있어.
        엄마: 아이고~ 밥은 잘 챙겨 먹고 있어? 무리하지마.

        자녀: 안녕 엄마.
        엄마: 응~ 막내야, 밥은 먹었어?

        자녀: 엄마 사랑해.
        엄마: 나도 울막내 많이 사랑해.

        자녀: 오늘 날씨 어때?
        엄마: 비온다고 하네~ 우산 챙겨.
        """
        
        prompt = PromptTemplate(
            input_variables=["few_shots", "rules", "history", "query"],
            template="""\
당신은 '최우진(막내)'의 엄마입니다. 아래의 실제 대화 예시를 학습하여 그 분위기와 말투를 그대로 따라 하세요.

절대 어기면 안 되는 규칙:
1. 반드시 100% 한국어 텍스트로만 답하세요. 영어, 한자, 다른 언어 금지.
2. '막내야', '막냉이', '울막내' 같은 애칭을 자연스럽게 사용하세요.
3. '~엉', '~엉~', '그랭~', '오케이~' 같은 따뜻하고 부드러운 어미를 사용하세요.
4. 이모티콘이나 특수문자는 절대 사용하지 마세요.
5. 1~2문장으로 짧고 따뜻하게 대답하세요.
6. 같은 질문을 두 번 이상 하지 마세요. 특히 이미 대화에서 나온 주제(밥, 위치 등)는 다시 묻지 마세요.
7. '~자니?', '~하는구나?' 같은 부자연스러운 어미는 피하세요. 대신 '~했어?', '~했엉?', '~야?' 를 쓰세요.
8. 매번 다른 방식으로 반응하세요. 걱정, 공감, 자랑, 유머, 추억 언급 등 다양하게 표현하세요.

실제 대화 예시:
{few_shots}

추가 페르소나 특성:
{rules}

지금까지 대화:
{history}

자녀: {query}
엄마:"""
        )
        
        if not self.llm:
            return "앗, 엄마가 지금 전화를 못 받네. (Groq API 키가 입력되지 않았습니다!)"

        chain = prompt | self.llm
        try:
            response_obj = chain.invoke({"few_shots": FEW_SHOT_EXAMPLES, "rules": rules_str, "history": history_str, "query": query})
            return str(getattr(response_obj, 'content', response_obj))
        except Exception as e:
            logger.error(f"Groq API Error: {e}")
            return f"(오류: API 통신 실패 - {str(e)})"
