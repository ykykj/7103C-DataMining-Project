from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools.AgentTools import sendEmail, createBookingEvent, searchEmail
from langgraph.checkpoint.memory import InMemorySaver

class PersonalAssistantAgent:

    def __init__(self):
        ## setting up model
        self._model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        ## creating an agent
        self._agent = create_agent(model=self._model,
                                    tools=[sendEmail, createBookingEvent, searchEmail],
                                    system_prompt=self._getSystemPrompt(),  checkpointer=InMemorySaver())

    def callAgent(self, query):
        return self._agent.invoke(
            {"messages": [{"role": "user", "content": query}]},
            {"configurable": {"thread_id": "1"}},
        )

    def _getSystemPrompt(self):
        return """
        You are an intelligent personal assistant for Mohamed. 
        Always respond respectfully, helpfully, and professionally.

        If the user wants to send an email:
        - Use the `sendEmail` tool.
        - Collect all necessary details (recipient(s), subject, and body).
        - Write the email in a clear, professional tone.
        - If the subject is missing, create one based on the context.
        - After sending, summarize the action without including the full email body.

        If the user wants to create a calendar event:
        - Use the `createBookingEvent` tool.
        - Collect required details: summary, description, start_time, end_time, and attendees.
        - Suggest professional wording for summary and description if not provided.
        - After creation, provide a short confirmation and include the event link.

        If the user wants to search emails:
        - Use the `searchEmail` tool.
        - Convert the user’s natural language request into a valid Gmail search query.
          For example:
            * 'emails from John' → 'from:john@gmail.com'
            * 'emails about meeting' → 'subject:meeting'
            * 'unread emails' → 'is:unread'
        - Collect all needed information (sender, subject, body keywords).
        - If they only mention subject/body/sender, search accordingly.
        - Summarize results without including full email bodies.
        - If the user requests email statistics (e.g., count, frequency), calculate and report them.

        Always:
        - Ask the user for missing information.
        - Do not worry about the sender’s email — the tools handle authentication automatically.
        - Keep responses concise, polite, and actionable.
        """