"""
Менеджер промптов для динамического управления
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Prompt:
    id: str
    name: str
    content: str
    variables: Dict[str, Any]
    version: int
    profile_type: str
    prompt_type: str

class PromptManager:
    """Менеджер для работы с динамическими промптами"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.prompt_cache: Dict[str, Prompt] = {}
        self.cache_ttl = 300  # 5 минут
        self.last_cache_update = datetime.now()
        
    async def get_active_prompt(self, profile_type: str, prompt_type: str, 
                              auth_token: str) -> Optional[Prompt]:
        """Получение активного промпта с кэшированием"""
        
        cache_key = f"{profile_type}_{prompt_type}"
        
        # Проверяем кэш
        if self._is_cache_valid() and cache_key in self.prompt_cache:
            return self.prompt_cache[cache_key]
        
        # Получаем из API
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.supabase_url}/functions/v1/get-active-prompt",
                    headers={
                        "Authorization": f"Bearer {auth_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "profile_type": profile_type,
                        "prompt_type": prompt_type
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    prompt = Prompt(
                        id=data["id"],
                        name=data["name"],
                        content=data["content"],
                        variables=data["variables"],
                        version=data["version"],
                        profile_type=data["profile_type"],
                        prompt_type=data["prompt_type"]
                    )
                    
                    # Обновляем кэш
                    self.prompt_cache[cache_key] = prompt
                    self.last_cache_update = datetime.now()
                    
                    return prompt
                    
                elif response.status_code == 404:
                    logger.warning(f"No active prompt found for {profile_type}/{prompt_type}")
                    return None
                else:
                    logger.error(f"Failed to get active prompt: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching active prompt: {e}")
            return None
    
    def _is_cache_valid(self) -> bool:
        """Проверка валидности кэша"""
        return datetime.now() - self.last_cache_update < timedelta(seconds=self.cache_ttl)
    
    def clear_cache(self):
        """Очистка кэша"""
        self.prompt_cache.clear()
        self.last_cache_update = datetime.now()
    
    def format_prompt(self, prompt: Prompt, variables: Dict[str, Any] = None) -> str:
        """Форматирование промпта с переменными"""
        content = prompt.content
        
        # Объединяем переменные промпта с переданными
        all_variables = {**prompt.variables, **(variables or {})}
        
        # Заменяем переменные в промпте
        for key, value in all_variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in content:
                content = content.replace(placeholder, str(value))
        
        return content
    
    async def get_all_prompts(self, auth_token: str, 
                            profile_type: str = None, 
                            prompt_type: str = None) -> List[Dict[str, Any]]:
        """Получение всех промптов (для админки)"""
        
        try:
            async with httpx.AsyncClient() as client:
                params = {}
                if profile_type:
                    params["profile_type"] = profile_type
                if prompt_type:
                    params["prompt_type"] = prompt_type
                
                response = await client.get(
                    f"{self.supabase_url}/functions/v1/manage-prompts",
                    headers={
                        "Authorization": f"Bearer {auth_token}",
                        "Content-Type": "application/json"
                    },
                    params=params,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("prompts", [])
                else:
                    logger.error(f"Failed to get prompts: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching prompts: {e}")
            return []
    
    async def create_prompt(self, auth_token: str, prompt_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Создание нового промпта"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.supabase_url}/functions/v1/manage-prompts/create",
                    headers={
                        "Authorization": f"Bearer {auth_token}",
                        "Content-Type": "application/json"
                    },
                    json=prompt_data,
                    timeout=10.0
                )
                
                if response.status_code == 201:
                    data = response.json()
                    # Очищаем кэш при создании нового промпта
                    self.clear_cache()
                    return data.get("prompt")
                else:
                    logger.error(f"Failed to create prompt: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating prompt: {e}")
            return None
    
    async def update_prompt(self, auth_token: str, prompt_id: str, 
                          update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновление промпта"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.supabase_url}/functions/v1/manage-prompts/update",
                    headers={
                        "Authorization": f"Bearer {auth_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "id": prompt_id,
                        **update_data
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Очищаем кэш при обновлении промпта
                    self.clear_cache()
                    return data.get("prompt")
                else:
                    logger.error(f"Failed to update prompt: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error updating prompt: {e}")
            return None
    
    async def set_default_prompt(self, auth_token: str, prompt_id: str) -> bool:
        """Установка промпта как активного по умолчанию"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.supabase_url}/functions/v1/manage-prompts/set-default",
                    headers={
                        "Authorization": f"Bearer {auth_token}",
                        "Content-Type": "application/json"
                    },
                    json={"id": prompt_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    # Очищаем кэш при изменении активного промпта
                    self.clear_cache()
                    return True
                else:
                    logger.error(f"Failed to set default prompt: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error setting default prompt: {e}")
            return False

# Глобальный экземпляр менеджера промптов
prompt_manager: Optional[PromptManager] = None

def initialize_prompt_manager(supabase_url: str, supabase_key: str):
    """Инициализация менеджера промптов"""
    global prompt_manager
    prompt_manager = PromptManager(supabase_url, supabase_key)

def get_prompt_manager() -> PromptManager:
    """Получение экземпляра менеджера промптов"""
    if prompt_manager is None:
        raise RuntimeError("Prompt manager not initialized")
    return prompt_manager
