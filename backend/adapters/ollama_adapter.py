import json
from time import sleep
from typing import Optional, List
from pathlib import Path

import httpx
from httpx import TimeoutException

from ..core.logger import logger


class OllamaAdapter:
    def __init__(self):
        self.config = self._load_config()
        self.base_url = self.config["models"][0]["base_url"]
        self.model = self.config["default_model"]
        self.timeout = self.config["models"][0]["timeout"]
        self.max_retries = self.config["models"][0]["max_retries"]

    def _load_config(self) -> dict:
        """加载模型配置文件"""
        config_path = Path(__file__).parent.parent / "core" / "model_config.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载模型配置文件失败: {str(e)}")
            raise

    def list_models(self) -> List[str]:
        """获取可用模型列表"""
        try:
            return [model["name"] for model in self.config["models"]]
        except Exception as e:
            logger.error(f"获取模型列表失败: {str(e)}")
            return []

    def generate(self, prompt: str) -> str:
        """使用Ollama生成响应"""
        url = f"{self.base_url}/api/generate"
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }

        logger.info(f"Ollama API调用开始 - URL: {url}, 模型: {self.model}")
        logger.debug(f"提示词: {prompt}")
        response_text = ""
        for attempt in range(self.max_retries):
            try:
                with httpx.stream(
                    "POST",
                    url,
                    json=data,
                    headers={"Content-Type":"application/json"},
                    timeout=self.timeout
                ) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)
                            if chunk.get("response"):
                                chunk_response = chunk["response"]
                                response_text += chunk_response
                                print(chunk_response, end="", flush=True)  # 立即打印响应片段
                                logger.debug(f"收到响应片段: {chunk_response}")
                        except json.JSONDecodeError:
                            continue
                return response_text
            except TimeoutException:
                if attempt == self.max_retries - 1:
                    error_msg = f"Ollama API调用超时(已重试{self.max_retries}次)，请检查服务负载或增加超时时间"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                sleep(1)  # 重试前等待1秒
                continue
            except httpx.ConnectError:
                error_msg = "无法连接到Ollama服务，请确保服务已启动且端口11434可访问"
                logger.error(error_msg)
                raise Exception(error_msg)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    error_msg = "Ollama服务未响应，请检查服务是否正常运行"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                error_msg = f"Ollama API调用失败: HTTP {e.response.status_code}"
                logger.error(error_msg)
                raise Exception(error_msg)
            except Exception as e:
                error_msg = f"Ollama API调用失败: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg)

    def set_model(self, model_name: str) -> None:
        """设置要使用的模型"""
        # 验证模型是否存在
        if model_name not in self.list_models():
            error_msg = f"模型 {model_name} 不存在"
            logger.error(error_msg)
            raise ValueError(error_msg)
        self.model = model_name
        # 更新配置
        for model in self.config["models"]:
            if model["name"] == model_name:
                self.base_url = model["base_url"]
                self.timeout = model["timeout"]
                self.max_retries = model["max_retries"]
                break