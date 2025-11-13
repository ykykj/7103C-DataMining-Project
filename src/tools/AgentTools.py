from datetime import datetime

from langchain.tools import tool
from src.service.GoogleService import GoogleService



googleService = GoogleService()

@tool
def sendEmail(to_list: str, subject: str, message_text: str):
    """
    Sends an email to the specified recipient.

    Parameters:
    ----------
    to : str
        The recipient's email address (e.g., "someone@example.com" as a list
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
    if len(to_list) == 1:
        to = to_list[0]
    else:
        to = to_list.join(" ,")

    googleService.sendEmail(to, subject, message_text)
    return "Sent an email to {}".format(to)

@tool
def createBookingEvent(summary : str, description : str, start_time : datetime, end_time : datetime, attendees_emails_list=None):
    """
        Creates a Google Calendar event.

        Parameters:
        ----------
            summary : Summary of the event
            description : Description of the event
            start_time : Start time of the event
            end_time : End time of the event
            attendees_emails_list : List of attendee emails
    """
    return googleService.createBookingEvent(summary, description, start_time, end_time, attendees_emails_list)