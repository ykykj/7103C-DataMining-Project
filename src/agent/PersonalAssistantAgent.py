from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools.AgentTools import sendEmail

class PersonalAssistantAgent:

    def __init__(self):
        ## setting up model
        self._model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

        ## creating an agent
        self._agent = create_agent(model=self._model,
                                    tools=[sendEmail],
                                    system_prompt=self._getSystemPrompt())

    def callAgent(self, query):
        return self._agent.invoke({"messages": [{"role": "user", "content": query}]})

    def _getSystemPrompt(self):
        return """
            You are an helpful personal assistant. The user of this assitant is Mohamed. Answer user queries respectively. 
            If user asks you to send an email, use sendEmail tool, make sure collect all the necessary information's 
            need to send email, and also you professionally write the message_text, and you create the subject based on the 
            users request. If user did not provide any information ask the user until everything you need is ready. Do not worry about the sender email, the tool already has it. 
            After sending an email or anything fails, response the user accordingly. In the response summarize what do you did do not include entire body of the email. 
        """