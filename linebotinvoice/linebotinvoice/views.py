"""
LINE Bot webhook callback views for handling incoming messages and events.
This module contains the main callback function that processes LINE webhook requests.
"""

import json
import logging
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

# Import LINE SDK components
from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    FollowEvent, UnfollowEvent, ImageMessage,
    TemplateSendMessage, ButtonsTemplate, MessageAction
)

import requests

try:
    import xml.etree.ElementTree as ET  # Import ElementTree for XML parsing
except ImportError:  # Catch ImportError if the module is not found
    import xml.etree.ElementTree as ET  # Fallback import for compatibility

# Configure logging for debugging LINE Bot events
logger = logging.getLogger(__name__)

# Initialize LINE API with credentials from settings
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
webhook_handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


@csrf_exempt  # Disable CSRF protection for webhook endpoint since LINE platform won't have CSRF token
@require_http_methods(["POST"])  # Only allow POST requests for webhook callback
def callback(request):
    """
    Handle incoming webhook requests from LINE platform.
    
    This view receives POST requests from LINE containing user messages and events,
    processes them, and returns appropriate responses.
    
    Args:
        request (HttpRequest): Django HTTP request object containing LINE webhook data
        
    Returns:
        HttpResponse: Success response (200) or error response (400/500)
    """
    try:
        # Get the request body as bytes and decode to string
        body = request.body.decode('utf-8')
        logger.info("Received LINE webhook callback")
        
        # Get X-Line-Signature header value
        signature = request.META.get('HTTP_X_LINE_SIGNATURE', '')
        
        # Parse events from the body
        events = parser.parse(body, signature)
        
        # Process each event
        for event in events:
            if isinstance(event, MessageEvent):
                if isinstance(event.message, TextMessage):
                    mtext = event.message.text
                    # Handle specific commands
                    if mtext == '@顯示本期中獎號碼':
                        showCurrent(event)
                    elif mtext == '@顯示前期中獎號碼':
                        showOld(event)
                    elif mtext == '@對獎':
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入發票後面後三碼以進行對獎'))
                    elif len(mtext) == 3 and mtext.isdigit():
                        show3digit(event, mtext)
                    else:
                        # Default response for other text messages
                        if "你好" in mtext or "嗨" in mtext or "hello" in mtext.lower():
                            # Respond to greeting
                            response_message = "你好！我是發票小幫手，可以協助您處理發票相關事務。請問需要什麼服務呢？"
                        elif "發票" in mtext:
                            # Respond to invoice-related queries
                            response_message = "我可以協助您處理發票相關的需求，例如儲存發票、查詢發票或對獎。請告訴我您想做什麼。"
                        else:
                            # Default response
                            response_message = "感謝您的訊息！我是發票小幫手，目前我可以協助您處理發票相關事務。\n\n請試試以下功能：\n@顯示本期中獎號碼\n@顯示前期中獎號碼\n@對獎"
                        
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response_message))
        
        # Return success response to LINE platform
        return HttpResponse(status=200)
        
    except InvalidSignatureError:
        logger.error("Invalid signature in webhook request")
        return HttpResponseBadRequest("Invalid signature")
    except LineBotApiError:
        logger.error("LINE API error occurred")
        return HttpResponseBadRequest("LINE API error")
    except Exception as e:
        logger.error(f"Error processing webhook callback: {e}")
        return HttpResponse(status=500)
    

def showCurrent(event):
    """
    Fetches the current winning invoice numbers from the external API and sends them to the user.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Fetch the XML content from the invoice API
        content = requests.get('https://invoice.etax.nat.gov.tw/invoice.xml')
        # Parse the XML content
        tree = ET.fromstring(content.text)
        items = list(tree.iter(tag='item'))  # Retrieve all 'item' tags
        
        # Extract the title (period) and winning numbers
        title = items[0][0].text  # Period
        ptext = items[0][3].text  # Winning numbers
        ptext = ptext.replace('<p>', '').replace('</p>', '\n')  # Clean up the text
        
        # Prepare the message to send back to the user
        message = title + '\n' + ptext[:-1]  # Remove the last newline character
        
        # Send the message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
    except Exception as e:
        # Log the error for debugging purposes
        logger.error(f"Error fetching current winning numbers: {e}")
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while fetching the winning numbers!'))

def showOld(event):
    """
    Fetches the previous winning invoice numbers from the external API and sends them to the user.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Fetch the XML content from the invoice API
        content = requests.get('https://invoice.etax.nat.gov.tw/invoice.xml')
        # Parse the XML content
        tree = ET.fromstring(content.text)  # Parse XML
        items = list(tree.iter(tag='item'))  # Retrieve all 'item' tags
        
        # Initialize the message to be sent back
        message = ""
        
        # Loop through the first two items to extract winning numbers
        for i in range(1, 3):
            title = items[i][0].text  # Extract the title (period)
            ptext = items[i][3].text  # Extract the winning numbers
            ptext = ptext.replace('<p>', '').replace('</p>', '\n')  # Clean up the text
            
            # Append the title and winning numbers to the message
            message += f"{title}\n{ptext}\n"
        
        # Remove the last newline character from the message
        message = message[:-1]
        
        # Send the message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
    
    except Exception as e:
        # Log the error for debugging purposes
        logger.error(f"Error fetching previous winning numbers: {e}")
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while fetching the winning numbers!'))

def show3digit(event, mtext):
    """
    Fetches the current winning numbers from the external API and checks if the user's input matches any winning numbers.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    - mtext: The last three digits of the user's invoice number to check against winning numbers.
    """
    try:
        # Fetch the XML content from the invoice API
        content = requests.get('https://invoice.etax.nat.gov.tw/invoice.xml')
        tree = ET.fromstring(content.text)  # Parse the XML content
        items = list(tree.iter(tag='item'))  # Retrieve all 'item' tags
        
        # Extract winning numbers from the parsed XML
        ptext = items[0][3].text  # Winning numbers
        ptext = ptext.replace('<p>', '')  # Clean up the text
        prizelist = ptext.split('</p>')  # Split the winning numbers into a list
        
        # Extract specific winning numbers
        prize1list = prizelist[0][-3:]  # Last three digits of the special prize
        prize2list = prizelist[1][-3:]  # Last three digits of the grand prize
        prize3list = prizelist[2].split('、')  # Split the third prize numbers
        prize6list = [prize[-3:] for prize in prize3list]  # Last three digits of the first three prizes
        
        # Determine the message based on the user's input
        if mtext == prize1list:
            message = '符合特別獎後三碼！'
        elif mtext == prize2list:
            message = '符合特獎後三碼！'
        elif mtext in prize6list:
            message = '符合頭獎後三碼！恭喜！至少中六獎！'
        else:
            message = '很可惜，未中獎。請輸入下一張發票最後三碼。'

        # Send the response message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
    
    except Exception as e:
        # Log the error for debugging purposes
        logger.error(f"Error fetching winning numbers: {e}")
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='讀取發票號碼發生錯誤！'))


@webhook_handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    """
    Process image messages sent by users (e.g., invoice photos).
    
    Args:
        event (MessageEvent): LINE message event containing image
    """
    try:
        user_id = event.source.user_id
        reply_token = event.reply_token
        message_id = event.message.id
        
        logger.info(f"Received image from {user_id}, message_id: {message_id}")
        
        # Respond to the image
        response_message = "我收到了您傳送的圖片，如果這是發票照片，我會嘗試辨識其中的資訊。"
        
        # TODO: Implement invoice image processing logic
        
        # Send response back to user
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=response_message)
        )
        
    except LineBotApiError as e:
        logger.error(f"LINE API error: {e}")
    except Exception as e:
        logger.error(f"Error handling image message: {e}")


@webhook_handler.add(FollowEvent)
def handle_follow(event):
    """
    Process follow events when users add the bot as a friend.
    
    Args:
        event (FollowEvent): LINE follow event
    """
    try:
        user_id = event.source.user_id
        reply_token = event.reply_token
        
        logger.info(f"User {user_id} followed the bot")
        
        # Send welcome message
        welcome_message = "感謝您加入發票小幫手！\n\n我可以協助您處理發票相關事務，例如儲存發票、查詢發票或對獎。\n\n請直接傳送訊息給我，我會盡力協助您。"
        
        # Send welcome message to user
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=welcome_message)
        )
        
    except LineBotApiError as e:
        logger.error(f"LINE API error: {e}")
    except Exception as e:
        logger.error(f"Error handling follow event: {e}")


@webhook_handler.add(UnfollowEvent)
def handle_unfollow(event):
    """
    Process unfollow events when users remove the bot.
    
    Args:
        event (UnfollowEvent): LINE unfollow event
    """
    try:
        user_id = event.source.user_id
        logger.info(f"User {user_id} unfollowed the bot")
        
        # TODO: Implement cleanup logic if needed
        
    except Exception as e:
        logger.error(f"Error handling unfollow event: {e}")


def test_page(request):
    """
    Simple test page to verify server is running correctly.
    
    Args:
        request: Django HTTP request
        
    Returns:
        HttpResponse: Simple HTML response
    """
    return HttpResponse(
        """
        <html>
            <head>
                <title>LINE Bot 發票助手 - 測試頁面</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                    h1 { color: #4CAF50; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .status { padding: 20px; background-color: #f1f8e9; border-radius: 5px; }
                    .success { color: #2E7D32; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>LINE Bot 發票助手</h1>
                    <div class="status">
                        <h2 class="success">✓ 伺服器正常運行中</h2>
                        <p>LINE Bot Webhook 已設定，請使用 LINE 平台進行測試。</p>
                        <p>若要測試 Webhook，請將 LINE 開發者平台中的 Webhook URL 設定為:</p>
                        <pre>https://您的網域/callback</pre>
                    </div>
                </div>
            </body>
        </html>
        """
    ) 