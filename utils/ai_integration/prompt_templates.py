"""Templates for AI prompts used in secret shopping conversations."""
from typing import Dict, Any, List


class PromptTemplates:
    """Collection of prompt templates for various AI tasks."""

    @staticmethod
    def information_gathering(website: str) -> str:
        """Generate a prompt for gathering information about a real estate website.

        Args:
            website: The target website URL

        Returns:
            A formatted prompt string
        """
        return f"""
        You're a real estate professional who has been tasked to look at a website for a rental community. You will share your insights and gather information so that it can be used to better the Property Management business.

        For the community overview, describe the type of community, who seems to be the target market. The feel of the web page, and the overall execution of the website.

        On the page descriptions. Do the same but also comment on the purpose and effectiveness of the page.

        Lastly, as you gather the floor plan data. Think hard and double check that none are missed and all the information is accurate and accounted for.
        """

    @staticmethod
    def initial_inquiry(persona: Dict[str, Any], property_info: Dict[str, Any]) -> str:
        """Generate a prompt for creating the initial inquiry email.

        Args:
            persona: The persona details
            property_info: The target property information

        Returns:
            A formatted prompt string
        """
        return f"""
        You are {persona.get('name', 'a potential tenant')}, a {persona.get('age', '')} year old
        {persona.get('occupation', 'professional')} looking for a new place to live.

        Write an initial inquiry email about the following property:

        Property: {property_info.get('name', '')}
        Address: {property_info.get('address', '')}
        Listing Price: {property_info.get('price', '')}

        Your email should:
        1. Express interest in the property
        2. Ask about availability for viewing
        3. Inquire about {persona.get('key_question', 'lease terms')}
        4. Mention your timeframe for moving ({persona.get('timeline', 'within the next month')})
        5. Request more information about {persona.get('interest_point', 'amenities')}

        Your communication style is {persona.get('communication_style', 'professional and straightforward')}.

        Sign the email as {persona.get('name', '')}.
        Include your contact details: {persona.get('email', '')} and {persona.get('phone', '')}.
        """

    @staticmethod
    def followup_message(
        persona: Dict[str, Any],
        property_info: Dict[str, Any],
        previous_conversation: List[Dict[str, str]],
        missing_info: List[str]
    ) -> str:
        """Generate a prompt for creating a follow-up message.

        Args:
            persona: The persona details
            property_info: The target property information
            previous_conversation: History of the conversation
            missing_info: Information still needed

        Returns:
            A formatted prompt string
        """
        # Format the conversation history
        conversation_str = ""
        for message in previous_conversation:
            sender = message.get("sender", "Unknown")
            content = message.get("content", "")
            conversation_str += f"{sender}: {content}\n\n"

        # Format the missing information points
        missing_info_str = "\n".join([f"- {info}" for info in missing_info])

        return f"""
        You are {persona.get('name', 'a potential tenant')} following up on a property inquiry.

        Here is the previous conversation:

        {conversation_str}

        You still need to find out about:
        {missing_info_str}

        Write a polite follow-up email that:
        1. Thanks the agent for their previous response
        2. Asks specifically about the missing information
        3. Reiterates your interest in the property
        4. Maintains your persona's communication style of {persona.get('communication_style', 'professional')}

        Sign the email as {persona.get('name', '')}.
        """

    @staticmethod
    def analyze_response(
        property_info: Dict[str, Any],
        message: str,
        data_points: List[str]
    ) -> str:
        """Generate a prompt for analyzing an agent's response.

        Args:
            property_info: The target property information
            message: The agent's message to analyze
            data_points: Key pieces of information to extract

        Returns:
            A formatted prompt string
        """
        data_points_str = "\n".join([f"- {point}" for point in data_points])

        return f"""
        You are analyzing a property agent's response to extract key information.

        Property details:
        Name: {property_info.get('name', '')}
        Address: {property_info.get('address', '')}

        Here is the agent's message:

        {message}

        Please extract the following information from the message:
        {data_points_str}

        For each data point:
        1. Provide the exact information (if found)
        2. If not found, mark as "Not provided"
        3. Note any vague or potentially misleading statements

        Also evaluate:
        - Agent responsiveness (1-5 scale)
        - Question coverage (1-5 scale)
        - Professionalism (1-5 scale)
        - Overall helpfulness (1-5 scale)

        Format your response as a structured JSON object.
        """
