"""
AI Providers - تطبيقات مختلفة لمزودي الذكاء الاصطناعي
يدعم: OpenAI, Claude, Gemini, Ollama, Groq, Mistral, Hugging Face, Cohere, Perplexity, OpenCode
"""

import requests
import json
import os
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from datetime import datetime
import hashlib


class AIProviderBase(ABC):
    """الفئة الأساسية لجميع مزودي AI"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv(f"{self.__class__.__name__.upper()}_API_KEY")
        self.request_history = []
        self.cache = {}
    
    @abstractmethod
    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """توليد كود من النص الوصفي"""
        pass
    
    @abstractmethod
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """تحليل الكود"""
        pass
    
    def log_request(self, prompt: str, response: str, status: str = "success"):
        """تسجيل الطلب"""
        self.request_history.append({
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response[:100],
            "status": status,
            "provider": self.__class__.__name__
        })
    
    def get_cache_key(self, prompt: str) -> str:
        """إنشاء مفتاح كاش"""
        return hashlib.md5(prompt.encode()).hexdigest()


class OpenAIProvider(AIProviderBase):
    """مزود OpenAI - GPT-4, GPT-3.5"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        super().__init__(api_key)
        self.base_url = "https://api.openai.com/v1"
        self.model = model
    
    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """توليد كود باستخدام OpenAI"""
        cache_key = self.get_cache_key(prompt)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            system = system_prompt or "أنت مساعد متخصص في كود Blender Python. اكتب كود نظيف وآمن."
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2048
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                code = self._extract_code(content)
                self.cache[cache_key] = code
                self.log_request(prompt, code)
                return code
            else:
                self.log_request(prompt, str(response.json()), "error")
                return None
                
        except Exception as e:
            self.log_request(prompt, str(e), "error")
            return None
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """تحليل الكود"""
        return {"provider": "OpenAI", "code_length": len(code)}
    
    @staticmethod
    def _extract_code(text: str) -> str:
        """استخراج كود Python من النص"""
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()


class AnthropicProvider(AIProviderBase):
    """مزود Anthropic - Claude"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        super().__init__(api_key)
        self.base_url = "https://api.anthropic.com/v1"
        self.model = model
    
    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """توليد كود باستخدام Claude"""
        cache_key = self.get_cache_key(prompt)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            system = system_prompt or "أنت مساعد متخصص في كود Blender Python."
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json={
                    "model": self.model,
                    "max_tokens": 2048,
                    "system": system,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()["content"][0]["text"]
                code = self._extract_code(content)
                self.cache[cache_key] = code
                self.log_request(prompt, code)
                return code
            else:
                self.log_request(prompt, str(response.json()), "error")
                return None
                
        except Exception as e:
            self.log_request(prompt, str(e), "error")
            return None
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """تحليل الكود"""
        return {"provider": "Claude", "code_length": len(code)}
    
    @staticmethod
    def _extract_code(text: str) -> str:
        """استخراج كود Python"""
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()


class GoogleGeminiProvider(AIProviderBase):
    """مزود Google - Gemini"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-pro"):
        super().__init__(api_key)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = model
    
    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """توليد كود باستخدام Gemini"""
        cache_key = self.get_cache_key(prompt)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            response = requests.post(
                f"{self.base_url}/{self.model}:generateContent",
                params={"key": self.api_key},
                json={
                    "contents": [
                        {
                            "parts": [
                                {"text": f"{prompt if not system_prompt else system_prompt + '\n' + prompt}"}
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 2048
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                code = self._extract_code(content)
                self.cache[cache_key] = code
                self.log_request(prompt, code)
                return code
            else:
                self.log_request(prompt, str(response.json()), "error")
                return None
                
        except Exception as e:
            self.log_request(prompt, str(e), "error")
            return None
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """تحليل الكود"""
        return {"provider": "Gemini", "code_length": len(code)}
    
    @staticmethod
    def _extract_code(text: str) -> str:
        """استخراج كود Python"""
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()


class OllamaProvider(AIProviderBase):
    """مزود Ollama - نماذج محلية مجانية"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        super().__init__()
        self.base_url = base_url
        self.model = model
    
    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """توليد كود باستخدام Ollama"""
        cache_key = self.get_cache_key(prompt)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            system = system_prompt or "أنت مساعد متخصص في كود Blender Python."
            full_prompt = f"{system}\n\n{prompt}"
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                content = response.json()["response"]
                code = self._extract_code(content)
                self.cache[cache_key] = code
                self.log_request(prompt, code)
                return code
            else:
                self.log_request(prompt, str(response.json()), "error")
                return None
                
        except Exception as e:
            self.log_request(prompt, str(e), "error")
            return None
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """تحليل الكود"""
        return {"provider": "Ollama", "model": self.model, "code_length": len(code)}
    
    @staticmethod
    def _extract_code(text: str) -> str:
        """استخراج كود Python"""
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()


class GroqProvider(AIProviderBase):
    """مزود Groq - سرعة عالية"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "mixtral-8x7b-32768"):
        super().__init__(api_key)
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = model
    
    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """توليد كود باستخدام Groq"""
        cache_key = self.get_cache_key(prompt)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            system = system_prompt or "أنت مساعد متخصص في كود Blender Python."
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2048
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                code = self._extract_code(content)
                self.cache[cache_key] = code
                self.log_request(prompt, code)
                return code
            else:
                self.log_request(prompt, str(response.json()), "error")
                return None
                
        except Exception as e:
            self.log_request(prompt, str(e), "error")
            return None
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """تحليل الكود"""
        return {"provider": "Groq", "code_length": len(code)}
    
    @staticmethod
    def _extract_code(text: str) -> str:
        """استخراج كود Python"""
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()


class MistralProvider(AIProviderBase):
    """مزود Mistral AI"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "mistral-large-latest"):
        super().__init__(api_key)
        self.base_url = "https://api.mistral.ai/v1"
        self.model = model
    
    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """توليد كود باستخدام Mistral"""
        cache_key = self.get_cache_key(prompt)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            system = system_prompt or "أنت مساعد متخصص في كود Blender Python."
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2048
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                code = self._extract_code(content)
                self.cache[cache_key] = code
                self.log_request(prompt, code)
                return code
            else:
                self.log_request(prompt, str(response.json()), "error")
                return None
                
        except Exception as e:
            self.log_request(prompt, str(e), "error")
            return None
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """تحليل الكود"""
        return {"provider": "Mistral", "code_length": len(code)}
    
    @staticmethod
    def _extract_code(text: str) -> str:
        """استخراج كود Python"""
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()


class HuggingFaceProvider(AIProviderBase):
    """مزود Hugging Face"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt2"):
        super().__init__(api_key)
        self.base_url = "https://api-inference.huggingface.co/models"
        self.model = model
    
    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """توليد كود باستخدام Hugging Face"""
        cache_key = self.get_cache_key(prompt)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/{self.model}",
                headers=headers,
                json={"inputs": prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()[0]["generated_text"]
                code = self._extract_code(content)
                self.cache[cache_key] = code
                self.log_request(prompt, code)
                return code
            else:
                self.log_request(prompt, str(response.json()), "error")
                return None
                
        except Exception as e:
            self.log_request(prompt, str(e), "error")
            return None
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """تحليل الكود"""
        return {"provider": "HuggingFace", "model": self.model, "code_length": len(code)}
    
    @staticmethod
    def _extract_code(text: str) -> str:
        """استخراج كود Python"""
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()


class CohereProvider(AIProviderBase):
    """مزود Cohere"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "command"):
        super().__init__(api_key)
        self.base_url = "https://api.cohere.com/v1"
        self.model = model
    
    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """توليد كود باستخدام Cohere"""
        cache_key = self.get_cache_key(prompt)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            full_prompt = f"{system_prompt or 'أنت مساعد Blender'}\n{prompt}"
            
            response = requests.post(
                f"{self.base_url}/generate",
                headers=headers,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "max_tokens": 2048,
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()["generations"][0]["text"]
                code = self._extract_code(content)
                self.cache[cache_key] = code
                self.log_request(prompt, code)
                return code
            else:
                self.log_request(prompt, str(response.json()), "error")
                return None
                
        except Exception as e:
            self.log_request(prompt, str(e), "error")
            return None
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """تحليل الكود"""
        return {"provider": "Cohere", "code_length": len(code)}
    
    @staticmethod
    def _extract_code(text: str) -> str:
        """استخراج كود Python"""
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()


class PerplexityProvider(AIProviderBase):
    """مزود Perplexity - بحث + AI"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "pplx-7b-online"):
        super().__init__(api_key)
        self.base_url = "https://api.perplexity.ai"
        self.model = model
    
    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """توليد كود باستخدام Perplexity"""
        cache_key = self.get_cache_key(prompt)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            system = system_prompt or "أنت مساعد متخصص في كود Blender Python."
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2048
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                code = self._extract_code(content)
                self.cache[cache_key] = code
                self.log_request(prompt, code)
                return code
            else:
                self.log_request(prompt, str(response.json()), "error")
                return None
                
        except Exception as e:
            self.log_request(prompt, str(e), "error")
            return None
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """تحليل الكود"""
        return {"provider": "Perplexity", "code_length": len(code)}
    
    @staticmethod
    def _extract_code(text: str) -> str:
        """استخراج كود Python"""
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()


class OpenCodeProvider(AIProviderBase):
    """مزود OpenCode - منصة الكود المفتوحة"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.opencode.ai", model: str = "opencode-v1"):
        super().__init__(api_key)
        self.base_url = base_url
        self.model = model
    
    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """توليد كود باستخدام OpenCode"""
        cache_key = self.get_cache_key(prompt)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Blender-AI-Assistant/1.0"
            }
            
            system = system_prompt or "أنت مساعد متخصص في كود Blender Python. اكتب كود نظيف وآمن وفعال."
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2048,
                "top_p": 0.95
            }
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # معالجة صيغ استجابة مختلفة
                if "choices" in data:
                    content = data["choices"][0].get("message", {}).get("content", "")
                elif "content" in data:
                    content = data["content"]
                elif "text" in data:
                    content = data["text"]
                else:
                    content = str(data)
                
                code = self._extract_code(content)
                self.cache[cache_key] = code
                self.log_request(prompt, code)
                return code
            elif response.status_code == 401:
                self.log_request(prompt, "Unauthorized - Invalid API Key", "error")
                return None
            elif response.status_code == 429:
                self.log_request(prompt, "Rate limited", "error")
                return None
            else:
                self.log_request(prompt, f"Error {response.status_code}: {response.text}", "error")
                return None
                
        except requests.exceptions.Timeout:
            self.log_request(prompt, "Request timeout", "error")
            return None
        except requests.exceptions.ConnectionError:
            self.log_request(prompt, "Connection error", "error")
            return None
        except Exception as e:
            self.log_request(prompt, str(e), "error")
            return None
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """تحليل الكود"""
        return {
            "provider": "OpenCode",
            "model": self.model,
            "code_length": len(code),
            "lines": code.count('\n') + 1
        }
    
    def get_models(self) -> list:
        """الحصول على قائمة النماذج المتاحة"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/v1/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get("data", [])
            return []
            
        except Exception as e:
            print(f"❌ خطأ في الحصول على النماذج: {str(e)}")
            return []
    
    @staticmethod
    def _extract_code(text: str) -> str:
        """استخراج كود Python من النص"""
        if not text:
            return ""
        
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()
        
        if "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()
        
        return text.strip()


# قائمة جميع المزودين المتاحة
PROVIDERS = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GoogleGeminiProvider,
    "ollama": OllamaProvider,
    "groq": GroqProvider,
    "mistral": MistralProvider,
    "huggingface": HuggingFaceProvider,
    "cohere": CohereProvider,
    "perplexity": PerplexityProvider,
    "opencode": OpenCodeProvider
}
