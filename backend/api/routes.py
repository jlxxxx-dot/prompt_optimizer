from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from typing import Optional, List
from ..core.optimizer import PromptOptimizer
from ..core.logger import logger

router = APIRouter()
optimizer = PromptOptimizer()

class PromptRequest(BaseModel):
    prompt: str
    template_id: Optional[str] = None
    options: Optional[dict] = None

class OptimizationResponse(BaseModel):
    original_prompt: str
    optimized_prompt: str
    template_used: Optional[str] = None

@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_prompt(request: PromptRequest):
    logger.info(f"收到优化请求 - 模板ID: {request.template_id if request.template_id else '无'}, 提示词长度: {len(request.prompt)}")
    
    try:
        optimized = optimizer.optimize_prompt(request.prompt, request.template_id)
        logger.info("提示词优化完成")
        
        return OptimizationResponse(
            original_prompt=request.prompt,
            optimized_prompt=optimized,
            template_used=request.template_id
        )
    except Exception as e:
        logger.error(f"提示词优化失败: {str(e)}")
        raise