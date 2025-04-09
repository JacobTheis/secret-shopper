"""Client for interacting with OpenAI's API for AI-driven conversations."""
import os
import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI
from django.conf import settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for OpenAI API interactions."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI client.

        Args:
            api_key: Optional API key. If not provided, uses OPENAI_API_KEY
            from settings.
        """
        self.api_key = api_key or os.environ.get(
            'OPENAI_API_KEY', settings.OPENAI_API_KEY)
        self.client = OpenAI(api_key=self.api_key)

    def generate_response(self,
                          prompt: str,
                          model: str = "gpt-4o-mini",
                          temperature: float = 1,
                          max_output_tokens: int = 5000,
                          tools: Optional[List[str]] = [],
                          tool_choice: Optional[str] = {}
                          ) -> str:
        """Generate a text response from the AI.

        Args:
            prompt: The input prompt for the AI
            model: The model to use
            temperature: Controls randomness (0-1)
            max_output_tokens: Maximum tokens in the response

        Returns:
            The generated text response
        """
        try:
            response = self.client.responses.create(
                model=model,
                input=[
                    {
                        "role": "system",
                        "content": {
                            "type": "input_text",
                            "text": prompt
                        }
                    }
                ],
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                tools=tools,
            )
            return response.output_text
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise

    def generate_persona(self,
                         template: Dict[str, Any],
                         target_property: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a persona based on the template and target property.

        Args:
            template: Template parameters for persona creation
            target_property: Information about the target property

        Returns:
            A dictionary containing the generated persona details
        """
        prompt = f"""
        Create a detailed persona for a secret shopper who will be inquiring
        about a rental property with these characteristics:

        Property: {target_property.get('name', 'Unknown')}
        Location: {target_property.get('location', 'Unknown')}
        Type: {target_property.get('type', 'Unknown')}
        Price Range: {target_property.get('price_range', 'Unknown')}

        The persona should follow this template:
        - Background: {template.get('background_type', 'Professional')}
        - Income Level: {template.get('income_level', 'Middle')}
        - Family Status: {template.get('family_status', 'Single')}
        - Move-in Timeline: {template.get('timeline', '1-2 months')}

        Include:
        1. Name
        2. Age
        3. Occupation
        4. Reason for moving
        5. Budget constraints
        6. Preferred amenities
        7. Brief communication style for emails
        """

        response = self.generate_response(
            prompt=prompt,
            model="gpt-4-turbo",
            temperature=0.8,
            max_output_tokens=1000
        )

        # Parse the response into a structured persona
        persona = self._parse_persona_response(response)
        return persona

    def _parse_persona_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response into a structured persona dictionary.

        This is a simplified implementation. In a real-world scenario, you
        might want to use regex or more sophisticated parsing for reliability.

        Args:
            response: The raw response from the AI

        Returns:
            A structured persona dictionary
        """
        lines = response.strip().split('\n')
        persona = {}

        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                persona[key.strip().lower().replace(' ', '_')] = value.strip()

        # Ensure key fields exist
        for field in [
            'name',
            'age',
            'occupation',
            'reason_for_moving',
            'budget'
        ]:
            persona.setdefault(field, "")

        return persona
