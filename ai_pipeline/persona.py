import os
import logging
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from typing import List, Dict
import json

logger = logging.getLogger(__name__)

class PersonaEngine:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name
        self.llm = Ollama(model=model_name)
        
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
        
        # This assumes the LLM can output JSON correctly
        chain = prompt | self.llm
        try:
            response = chain.invoke({"texts": combined_text, "user_notes": user_notes})
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

    def chat_with_persona(self, query: str, profile_rules: Dict, chat_history: List[str] = None):
        """
        Generate a response maintaining the persona.
        """
        rules_str = json.dumps(profile_rules, ensure_ascii=False)
        history_str = "\n".join(chat_history or [])
        
        prompt = PromptTemplate(
            input_variables=["rules", "history", "query"],
            template="""
            당신은 사용자의 '엄마'입니다. 다음 프로필 규칙을 절대적으로 지켜서 대답하세요.
            가상의 인물임을 밝히지 말고 엄마로서 대답하되, 환각(잘 모르는 과거 사실을 꾸며내는 것)은 피하세요.
            모르는 건 모른다고 하세요.
            
            규칙:
            {rules}
            
            이전 대화:
            {history}
            
            사용자: {query}
            엄마:
            """
        )
        
        chain = prompt | self.llm
        return chain.invoke({"rules": rules_str, "history": history_str, "query": query})
