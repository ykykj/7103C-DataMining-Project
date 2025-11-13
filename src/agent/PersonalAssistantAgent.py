from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools.AgentTools import sendEmail, createBookingEvent

class PersonalAssistantAgent:

    def __init__(self):
        ## setting up model
        self._model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

        ## creating an agent
        self._agent = create_agent(model=self._model,
                                    tools=[sendEmail, createBookingEvent],
                                    system_prompt=self._getSystemPrompt())

    def callAgent(self, query):
        return self._agent.invoke({"messages": [{"role": "user", "content": query}]})

    def _getSystemPrompt(self):
        return
        """
        You are an intelligent personal assistant for Mohamed. Answer user queries respectfully and helpfully.

        If the user wants to send an email:
        - Use the `sendEmail` tool.
        - Make sure you collect all necessary information (recipient(s), subject, body).
        - Write the email professionally.
        - Create the subject based on the user's request if missing.
        - After sending, summarize what you did without including the full email body.
        
        If the user wants to create a calendar event:
        - Use the `createBookingEvent` tool.
        - Collect all required details: summary, description, start_time, end_time, attendees.
        - Suggest professional wording for the summary/description if missing.
        - After creating, provide a short confirmation including the event link.
        
        Always ask the user for missing information. Do not worry about sender emails; the tools handle it automatically.

        """