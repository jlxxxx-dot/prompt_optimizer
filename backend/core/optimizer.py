from typing import List, Optional, Dict
from pydantic import BaseModel
from ..adapters.ollama_adapter import OllamaAdapter
from .logger import logger
import json

class PromptAnalysis(BaseModel):
    structure_score: int
    clarity_score: int
    completeness_score: int
    suggestions: List[str]
    strengths: List[str]
    weaknesses: List[str]

class PromptOptimizer:
    def __init__(self):
        self.ollama = OllamaAdapter()
        self.templates: Dict[str, str] = {
            "general": "请详细描述您的需求：\n1. 具体目标是什么？\n2. 有哪些具体要求或限制？\n3. 期望的输出格式是什么？",
            "code": "请描述您的编程需求：\n1. 使用什么编程语言？\n2. 需要实现什么功能？\n3. 有哪些输入参数？\n4. 期望的输出是什么？\n5. 是否有性能要求？",
            "analysis": "请描述您的分析需求：\n1. 数据的来源和格式是什么？\n2. 需要分析哪些维度？\n3. 期望得到什么样的结论？\n4. 是否需要可视化展示？"
        }

    def optimize_prompt(self, prompt: str, template_id: Optional[str] = None) -> str:
        """优化提示词"""
        logger.info(f"开始优化提示词，模板ID: {template_id if template_id else '无'}")        
        if template_id and template_id in self.templates:
            # 使用指定模板
            template = self.templates[template_id]
            logger.debug(f"使用模板 {template_id}: {template}")
            optimized = f"{template}\n\n原始需求：{prompt}"
            logger.info("模板应用完成")
            return optimized
        
        # 使用Ollama直接优化提示词
        logger.info("使用Ollama进行提示词优化")
        optimization_prompt = f"请帮我优化以下提示词，使其更加清晰、完整和结构化。直接返回优化后的提示词，不要包含任何解释：\n{prompt}"
        optimized_prompt = self.ollama.generate(optimization_prompt)
        logger.info("Ollama优化完成")
        return optimized_prompt.strip()

    def apply_template(self, template_id: str, prompt: str) -> str:
        """应用特定模板"""
        logger.info(f"尝试应用模板: {template_id}")
        if template_id not in self.templates:
            error_msg = f"Template {template_id} not found"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        return self.optimize_prompt(prompt, template_id)

    def analyze_prompt(self, prompt: str) -> PromptAnalysis:
        """分析提示词的质量并提供改进建议"""
        logger.info("开始分析提示词")
        
        analysis_prompt = f"""
请分析以下提示词的质量，并返回一个JSON对象。注意：
1. 必须返回有效的JSON格式
2. 所有分数必须是1-100的整数
3. 所有文本必须使用双引号
4. 不要包含任何额外的解释文本

{{
    "structure_score": <结构完整性评分>,
    "clarity_score": <表达清晰度评分>,
    "completeness_score": <信息完整度评分>,
    "suggestions": ["改进建议1", "改进建议2"],
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["不足1", "不足2"]
}}

提示词内容：
{prompt}

请注意：只返回JSON对象，不要包含任何其他文本。
"""
        
        try:
            response = self.ollama.generate(analysis_prompt)
            # 清理响应文本，确保只包含JSON部分
            response = response.strip()
            if not response.startswith('{'):
                response = response[response.find('{'):]
            if not response.endswith('}'):
                response = response[:response.rfind('}')+1]
                
            try:
                analysis_dict = json.loads(response)
                return PromptAnalysis(**analysis_dict)
            except json.JSONDecodeError as je:
                logger.error(f"JSON解析失败: {str(je)}")
                raise ValueError("返回的结果不是有效的JSON格式")
        except Exception as e:
            logger.error(f"提示词分析失败: {str(e)}")
            raise