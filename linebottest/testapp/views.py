# Import Django settings for retrieving configuration parameters used in view logic
from django.conf import settings

# Import HTTP response types for constructing appropriate responses to incoming requests
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden

# Import CSRF exemption decorator to allow webhook POSTs without a CSRF token
from django.views.decorators.csrf import csrf_exempt

# Import LINE Bot SDK core classes: LineBotApi to send replies, WebhookParser to parse incoming webhooks
from linebot import LineBotApi, WebhookParser

# Import exception classes: InvalidSignatureError for signature validation errors, LineBotApiError for API request failures
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, TextMessage, ImageSendMessage, StickerSendMessage

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

# /**************************************************
# Define the callback function to handle incoming webhook events
# **************************************************/
@csrf_exempt
def callback(request):
    # LINE webhook callback function to handle incoming messaging events.
    # CSRF exemption is applied to allow external POST requests without CSRF token.

    # Only accept POST requests for webhook calls, reject others
    if request.method != 'POST':
        return HttpResponseBadRequest()

    # Retrieve the signature header for request validation
    signature = request.META.get('HTTP_X_LINE_SIGNATURE', '')

    # Decode the raw request body into a UTF-8 string
    body = request.body.decode('utf-8')

    try:
        # Parse and verify the webhook payload
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        # Signature mismatch: unauthorized request
        return HttpResponseForbidden()
    except LineBotApiError:
        # Error occurred while interacting with LINE API
        return HttpResponseBadRequest()

    # Iterate through each event object parsed from the webhook payload
    for event in events:
        # Handle only message events to echo text messages
        if isinstance(event, MessageEvent):
            
            if isinstance(event.message, TextMessage):
                # Extract the text from the message
                mtext = event.message.text

                # Check the content of the message and respond accordingly
                if mtext == '@傳送文字':
                    
                    # default text message
                    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text='case 1'))
                    
                    # Show the custom text message
                    sendText(event)

                elif mtext == '@傳送圖片':
                    #line_bot_api.reply_message(event.reply_token, TextSendMessage(text='case 2'))
                    
                    sendImage(event)
                
                elif mtext == '@傳送貼圖':
                    #line_bot_api.reply_message(event.reply_token, TextSendMessage(text='case 3'))
                
                    sendStick(event)
                
                elif mtext == '@多項傳送':
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='case 4'))
                elif mtext == '@傳送位置':
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='case 5'))
                elif mtext == '@快速選單':
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='case 6'))
                else:
                    # Echo the received text message if no specific command is matched
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=mtext))

    # Acknowledge successful handling of the webhook event
    return HttpResponse()

def sendText(event):
    """
    Sends a text message in response to a LINE event.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Create a TextSendMessage object with the response text
        message = TextSendMessage(text="我是中原 Linebot,\n您好!")
        
        # Send the message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")
        
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='字發生錯誤!'))

def sendImage(event):
    """
    Sends an image message in response to a LINE event.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Create an ImageSendMessage object with the image URLs
        message = ImageSendMessage(
            #original_content_url="https://i.imgur.com/4QfKuz1.png",
            #preview_image_url="https://i.imgur.com/4QfKuz1.png"
            
            original_content_url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/640px-PNG_transparency_demonstration_1.png",
            preview_image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/640px-PNG_transparency_demonstration_1.png"
        )
        
        # Send the image message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")
        
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while sending the image!'))


def sendStick(event):
    """
    Sends a sticker message in response to a LINE event.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Create a StickerSendMessage object with the package and sticker IDs
        message = StickerSendMessage(
            package_id='446',
            sticker_id='1988'
        )
        
        # Send the sticker message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")
        
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while sending the sticker!'))