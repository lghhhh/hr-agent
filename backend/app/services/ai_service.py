import json
import httpx
from typing import Optional

from ..config import LLM_API_KEY, LLM_API_BASE, LLM_MODEL
from ..database import SessionLocal
from ..models.config import SystemConfig

# 系统级Prompt，可从数据库配置覆盖
DEFAULT_PROMPT = """你是一位专业的AI招聘面试分析师。请根据提供的面试对话全文，生成一份结构化的面试总结报告。

请严格按以下JSON格式输出，不要包含markdown标记：
{
    "summary_text": "一份完整的面试总结报告正文，使用中文自然语言分段描述，包括：候选人基本信息、核心技能匹配度、项目经验亮点、面试问答摘要、优势与不足、综合评估。要求语言流畅、段落清晰，适合面试官直接阅读。开头不要用'【'符号。",
    "candidate_name": "候选人姓名（从对话中提取）",
    "position": "应聘岗位",
    "work_years": "工作年限",
    "expected_salary": "期望薪资",
    "skill_match": "核心技能匹配度分析（2-3句话）",
    "project_highlights": "项目经验亮点与疑点（2-3点）",
    "qa_summary": "面试核心问答摘要（2-3个关键问答）",
    "strengths": "候选人优势（2-3点）",
    "weaknesses": "候选人不足/待确认项（2-3点）",
    "overall_assessment": "综合初评建议（2-3句话）"
}
如果对话中没有提到某些信息，请填写"未提及"。

注意：summary_text 必须是与结构化字段内容一致的完整中文报告正文，而非字段摘要。
"""


def _get_system_prompt() -> str:
    """从数据库获取自定义Prompt，如果未配置则使用默认值"""
    try:
        db = SessionLocal()
        config = db.query(SystemConfig).filter(
            SystemConfig.config_key == "ai_prompt"
        ).first()
        db.close()
        if config and config.config_value:
            return config.config_value
    except Exception:
        pass
    return DEFAULT_PROMPT


def _get_llm_config() -> tuple:
    """从数据库获取LLM配置，未配置则回退到环境变量。返回 (api_key, api_base, model)"""
    try:
        db = SessionLocal()
        key_cfg = db.query(SystemConfig).filter(
            SystemConfig.config_key == "llm_api_key"
        ).first()
        base_cfg = db.query(SystemConfig).filter(
            SystemConfig.config_key == "llm_api_base"
        ).first()
        model_cfg = db.query(SystemConfig).filter(
            SystemConfig.config_key == "llm_model"
        ).first()
        db.close()
        api_key = key_cfg.config_value if (key_cfg and key_cfg.config_value) else LLM_API_KEY
        api_base = base_cfg.config_value if (base_cfg and base_cfg.config_value) else LLM_API_BASE
        model = model_cfg.config_value if (model_cfg and model_cfg.config_value) else LLM_MODEL
        return api_key, api_base, model
    except Exception:
        return LLM_API_KEY, LLM_API_BASE, LLM_MODEL


async def generate_summary(
    dialogue_text: str,
    candidate_name: str = "",
    position_name: str = "",
) -> Optional[dict]:
    """调用大模型API生成面试总结"""
    api_key, api_base, model = _get_llm_config()
    if not api_key:
        return _mock_summary(dialogue_text, candidate_name, position_name)

    prompt = _get_system_prompt()

    user_content = f"候选人姓名：{candidate_name}\n应聘岗位：{position_name}\n\n面试对话全文：\n{dialogue_text}"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": user_content},
                    ],
                    "temperature": 0.3,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]

            # Try to parse JSON from response
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1] if "\n" in content else content
                content = content.rsplit("```", 1)[0] if "```" in content else content
                content = content.strip()

            result = json.loads(content)
            return result
    except Exception as e:
        print(f"AI调用失败: {e}")
        return _mock_summary(dialogue_text, candidate_name, position_name)


def _mock_summary(
    dialogue_text: str,
    candidate_name: str,
    position_name: str,
) -> dict:
    """当API未配置时返回模拟数据"""
    return {
        "summary_text": (
            f"候选人{candidate_name or '（待提取）'}应聘{position_name or '（待提取）'}岗位。\n\n"
            "（未配置AI API，以下为示例数据，请在系统设置中配置大模型API Key以启用AI自动解析。）\n\n"
            "核心技能匹配：请在系统设置中配置大模型API Key以启用AI自动解析。\n\n"
            "项目经验亮点：1. 配置API后可自动提取。2. 支持豆包、通义千问等模型。\n\n"
            "面试问答摘要：配置大模型API后自动生成面试问答摘要。\n\n"
            "优势：配置后可自动分析候选人优势。\n\n"
            "不足：配置后可自动分析候选人不足。\n\n"
            "综合评估：请在系统设置 -> 大模型配置中填写API信息后重试。"
        ),
        "candidate_name": candidate_name or "（待提取）",
        "position": position_name or "（待提取）",
        "work_years": "（未配置AI API，使用示例数据）",
        "expected_salary": "（未配置AI API，使用示例数据）",
        "skill_match": "请在系统设置中配置大模型API Key以启用AI自动解析。",
        "project_highlights": "1. 配置API后可自动提取\n2. 支持豆包、通义千问等模型",
        "qa_summary": "配置大模型API后自动生成面试问答摘要",
        "strengths": "配置后可自动分析候选人优势",
        "weaknesses": "配置后可自动分析候选人不足",
        "overall_assessment": "请在系统设置 -> 大模型配置中填写API信息后重试。",
    }
