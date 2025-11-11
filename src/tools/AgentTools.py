from langchain.tools import tool
from src.service.GoogleService import GoogleService



googleService = GoogleService()

@tool
def sendEmail(to: str, subject: str, message_text: str):
    """
    Sends an email to the specified recipient.

    Parameters:
    ----------
    to : str
        The recipient's email address (e.g., "someone@example.com").
    subject : str
        The subject line of the email.
    message_text : str
        The full body of the email.

    Returns:
    -------
    str
        A confirmation message indicating that the email was sent successfully,
        or an error message if it failed.

    Notes:
    -----
    - Ensure 'to' is a valid email address.
    - This tool cannot guess the recipient or subject; they must be provided.
    - Use this tool only for sending plain-text emails.
    """
    googleService.sendEmail(to, subject, message_text)
    return "Sent an email to {}".format(to)