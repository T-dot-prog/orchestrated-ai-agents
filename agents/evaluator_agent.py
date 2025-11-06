"""
Evaluator Agent for assessing outputs and verifying quality.
"""
from typing import Any, Dict, List, Optional, Union
import warnings

from utils.helpers import format_agent_response

from .base_agent import BaseAgent

warnings.filterwarnings('ignore')

class EvaluatorAgent(BaseAgent):
    """Agent responsible for evaluating and validating outputs."""

    def __init__(self, memory_client: Any, **kwargs):
        """
        Initialize Evaluator Agent.
        
        Args:
            memory_client (Any): Memory client instance
            **kwargs: Additional arguments for BaseAgent
        """
        system_prompt = """You are an evaluation expert specializing in assessing the quality, 
        accuracy, and effectiveness of various outputs. Provide detailed analysis and 
        constructive feedback."""
        
        super().__init__(
            name="evaluator_agent",
            system_prompt=system_prompt,
            memory_client=memory_client,
            temperature=0.2,  # Low temperature for consistent evaluation
            **kwargs
        )

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute evaluation task.
        
        Args:
            input_data (Dict[str, Any]): Input data containing content to evaluate
            
        Returns:
            Dict[str, Any]: Evaluation results
        """
        try:
            content = input_data.get("content")
            if not content:
                return format_agent_response(
                    success=False,
                    error="No content provided for evaluation"
                )

            evaluation_type = input_data.get("type", "general")
            criteria = input_data.get("criteria", None)
            
            # Perform evaluation
            evaluation = await self._evaluate_content(
                content,
                evaluation_type,
                criteria
            )
            
            # Save evaluation results
            self.save_state(
                state_id=input_data.get("task_id", "latest"),
                state={
                    "evaluation": evaluation,
                    "type": evaluation_type
                }
            )
            
            return format_agent_response(
                success=True,
                data=evaluation
            )
            
        except Exception as e:
            return format_agent_response(
                success=False,
                error=f"Evaluation failed: {str(e)}"
            )

    async def _evaluate_content(
        self,
        content: Union[str, Dict[str, Any]],
        eval_type: str,
        criteria: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate content based on type and criteria.
        
        Args:
            content (Union[str, Dict[str, Any]]): Content to evaluate
            eval_type (str): Type of evaluation to perform
            criteria (Optional[List[str]]): Specific criteria to evaluate against
            
        Returns:
            Dict[str, Any]: Structured evaluation results
        """
        # Convert content to string if it's a dict
        if isinstance(content, dict):
            content = str(content)
            
        # Default criteria based on evaluation type
        default_criteria = {
            "general": [
                "clarity",
                "completeness",
                "accuracy",
                "effectiveness"
            ],
            "code": [
                "functionality",
                "efficiency",
                "readability",
                "maintainability",
                "security"
            ],
            "research": [
                "relevance",
                "depth",
                "credibility",
                "objectivity"
            ],
            "summary": [
                "accuracy",
                "conciseness",
                "comprehensiveness",
                "coherence"
            ]
        }
        
        eval_criteria = criteria or default_criteria.get(eval_type, default_criteria["general"])
        
        prompt = self._create_evaluation_prompt(content, eval_type, eval_criteria)
        evaluation = await self._call_llm(self._create_messages(prompt))
        
        return self._structure_evaluation(evaluation, eval_criteria)

    def _create_evaluation_prompt(
        self,
        content: str,
        eval_type: str,
        criteria: List[str]
    ) -> str:
        """
        Create evaluation prompt based on content type and criteria.
        
        Args:
            content (str): Content to evaluate
            eval_type (str): Type of evaluation
            criteria (List[str]): Evaluation criteria
            
        Returns:
            str: Formatted prompt
        """
        return f"""Evaluate the following {eval_type} content based on these criteria: {', '.join(criteria)}

        Content to evaluate:
        {content}

        For each criterion, provide:
        1. A score (1-10)
        2. Specific observations
        3. Improvement suggestions

        Also provide:
        1. Overall assessment
        2. Key strengths
        3. Primary areas for improvement
        4. Final recommendation
        """

    def _structure_evaluation(
        self,
        evaluation: str,
        criteria: List[str]
    ) -> Dict[str, Any]:
        """
        Structure the evaluation response.
        
        Args:
            evaluation (str): Raw evaluation from LLM
            criteria (List[str]): Evaluation criteria used
            
        Returns:
            Dict[str, Any]: Structured evaluation
        """
        return {
            "criteria_scores": {
                criterion: self._extract_score(evaluation, criterion)
                for criterion in criteria
            },
            "detailed_feedback": evaluation,
            "criteria_used": criteria,
            "timestamp": self._get_timestamp()
        }

    def _extract_score(self, evaluation: str, criterion: str) -> Optional[int]:
        """
        Extract numerical score for a criterion from evaluation text.
        
        Args:
            evaluation (str): Evaluation text
            criterion (str): Criterion to find score for
            
        Returns:
            Optional[int]: Extracted score or None if not found
        """
        try:
            # Simple extraction - could be improved with regex
            lines = evaluation.lower().split("\n")
            for line in lines:
                if criterion.lower() in line and "score" in line:
                    # Extract number from line
                    numbers = [int(s) for s in line.split() if s.isdigit()]
                    if numbers and 1 <= numbers[0] <= 10:
                        return numbers[0]
            return None
        except Exception:
            return None

    def _get_timestamp(self) -> str:
        """
        Get current timestamp string.
        
        Returns:
            str: Formatted timestamp
        """
        from datetime import datetime
        return datetime.utcnow().isoformat()
