"""
Summarizer Agent for condensing and structuring information.
"""
from typing import Any, Dict, List

from utils.helpers import chunk_text, format_agent_response

from .base_agent import BaseAgent

class SummarizerAgent(BaseAgent):
    """Agent responsible for summarizing and structuring information."""

    def __init__(self, memory_client: Any, **kwargs):
        """
        Initialize Summarizer Agent.
        
        Args:
            memory_client (Any): Memory client instance
            **kwargs: Additional arguments for BaseAgent
        """
        system_prompt = """You are a summarization expert specializing in condensing complex 
        information into clear, structured summaries. Focus on extracting key points while 
        maintaining important context and details."""
        
        super().__init__(
            name="summarizer_agent",
            system_prompt=system_prompt,
            memory_client=memory_client,
            temperature=0.3,  # Lower temperature for more focused summaries
            **kwargs
        )

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute summarization task.
        
        Args:
            input_data (Dict[str, Any]): Input data containing text to summarize
            
        Returns:
            Dict[str, Any]: Structured summary
        """
        try:
            text = input_data.get("text")
            if not text:
                return format_agent_response(
                    success=False,
                    error="No text provided for summarization"
                )

            # Parameters for summarization
            mode = input_data.get("mode", "concise")  # concise, detailed, or bullet
            max_length = input_data.get("max_length", 1000)
            
            # Generate summary
            summary = await self._generate_summary(text, mode, max_length)
            
            # Save summary
            self.save_state(
                state_id=input_data.get("task_id", "latest"),
                state={"original_length": len(text), "summary": summary}
            )
            
            return format_agent_response(
                success=True,
                data={
                    "summary": summary,
                    "original_length": len(text),
                    "summary_length": len(summary["text"])
                }
            )
            
        except Exception as e:
            return format_agent_response(
                success=False,
                error=f"Summarization failed: {str(e)}"
            )

    async def _generate_summary(
        self,
        text: str,
        mode: str,
        max_length: int
    ) -> Dict[str, Any]:
        """
        Generate structured summary of text.
        
        Args:
            text (str): Text to summarize
            mode (str): Summarization mode (concise, detailed, or bullet)
            max_length (int): Maximum length of summary
            
        Returns:
            Dict[str, Any]: Structured summary
        """
        # Split long text into manageable chunks
        chunks = chunk_text(text)
        summaries = []
        
        for chunk in chunks:
            prompt = self._create_summary_prompt(chunk, mode, max_length)
            summary = await self._call_llm(self._create_messages(prompt))
            summaries.append(summary)
        
        # Combine summaries if needed
        if len(summaries) > 1:
            combined_prompt = self._create_combining_prompt(summaries, mode)
            final_summary = await self._call_llm(self._create_messages(combined_prompt))
        else:
            final_summary = summaries[0]
        
        return {
            "text": final_summary,
            "mode": mode,
            "chunks_processed": len(chunks)
        }

    def _create_summary_prompt(self, text: str, mode: str, max_length: int) -> str:
        """
        Create appropriate prompt based on summarization mode.
        
        Args:
            text (str): Text to summarize
            mode (str): Summarization mode
            max_length (int): Maximum length
            
        Returns:
            str: Formatted prompt
        """
        base_prompt = f"""Summarize the following text in {mode} mode, keeping it under {max_length} characters:

        {text}
        
        """
        
        if mode == "concise":
            base_prompt += "\nProvide a brief, high-level summary capturing the main points."
        elif mode == "detailed":
            base_prompt += "\nProvide a detailed summary with key points and supporting details."
        elif mode == "bullet":
            base_prompt += "\nProvide a bullet-point summary with main points and sub-points."
            
        return base_prompt

    def _create_combining_prompt(self, summaries: List[str], mode: str) -> str:
        """
        Create prompt for combining multiple summaries.
        
        Args:
            summaries (List[str]): List of summaries to combine
            mode (str): Summarization mode
            
        Returns:
            str: Combining prompt
        """
        combined_text = "\n\n".join([f"Summary {i+1}:\n{s}" for i, s in enumerate(summaries)])
        
        return f"""Combine the following summaries into a single coherent {mode} summary:

        {combined_text}
        
        Ensure the final summary maintains consistency and flows naturally."""
