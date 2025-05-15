# Import Django settings for retrieving configuration parameters used in view logic
from django.conf import settings

# Import HTTP response types for constructing appropriate responses to incoming requests
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden

# Import CSRF exemption decorator to allow webhook POSTs without a CSRF token
from django.views.decorators.csrf import csrf_exempt

# Import LINE Bot SDK core classes: LineBotApi to send replies, WebhookParser to parse incoming webhooks
from linebot import LineBotApi, WebhookParser

# Import urllib.parse to parse query parameters
from urllib.parse import parse_qsl

# Import exception classes: InvalidSignatureError for signature validation errors, LineBotApiError for API request failures
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, TextMessage, ImageSendMessage, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction, AudioSendMessage, VideoSendMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction, URITemplateAction, PostbackTemplateAction, PostbackEvent, ConfirmTemplate

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
                    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text='case 4'))

                    sendMulti(event)
                
                elif mtext == '@傳送位置':
                    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text='case 5'))

                    sendPosition(event)

                elif mtext == '@快速選單':
                    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text='case 6'))

                    sendQuickreply(event)
                elif mtext == '@傳送聲音':
                    sendVoice(event)
                elif mtext == '@傳送影片':
                    sendVideo(event)
                elif mtext == '@按鈕樣板':
                    sendButton(event)
                elif mtext == '@確認樣板':
                    sendConfirm(event)
                elif mtext == '@yes':
                    sendYes (event)
                elif mtext == '@no':
                    sendNo(event)
                elif mtext == '@轉盤樣板':
                    sendCarousel(event)
                elif mtext == '@圖片轉盤':
                    sendImageCarousel(event)
                elif mtext == '@購買披薩':
                    sendPizza(event)
                else:
                    # Echo the received text message if no specific command is matched
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=mtext))


            if isinstance(event, PostbackEvent):  # Check if the event is a PostbackEvent
                backdata = dict(parse_qsl(event.postback.data))  # Parse the postback data into a dictionary
                if backdata.get('action') == 'buy':  # Check if the action is 'buy'
                    sendBack_buy(event, backdata)  # Call the sendBack_buy function with the event and backdata
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

def sendMulti(event):
    """
    Sends multiple types of messages (sticker, text, and image) in response to a LINE event.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Create a list of messages to send
        message = [
            # Send a sticker message
            StickerSendMessage(
                package_id='1',
                sticker_id='2'
            ),
            # Send a text message
            TextSendMessage(
                text="這是 Pizza 圖片!"
            ),
            # Send an image message
            ImageSendMessage(
                original_content_url="https://i.imgur.com/4QfKuz1.png",
                preview_image_url="https://i.imgur.com/4QfKuz1.png"
            )
        ]
        
        # Send the list of messages using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")
        
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while sending the messages!'))

def sendPosition(event):
    """
    Sends a location message in response to a LINE event.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Create a LocationSendMessage object with the title, address, latitude, and longitude
        message = LocationSendMessage(
            title='北京大學',
            address='中國北京市海淀区颐和园路5号 邮政编码: 100871',
            latitude=39.98711025939518,  # Latitude
            longitude=116.30591681135664  # Longitude
        )
        
        # Send the location message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")
        
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while sending the location!'))

def sendQuickreply(event):
    """
    Sends a quick reply message in response to a LINE event.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Create a TextSendMessage object with quick reply options
        message = TextSendMessage(
            text='請選擇最喜歡的程式語言',
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=MessageAction(label="Python", text="Python")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="Java", text="Java")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="C#", text="C#")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="Basic", text="Basic")
                    )
                ]
            )
        )
        
        # Send the quick reply message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")
        
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while sending the quick reply!'))

def sendVoice(event):
    """
    Sends an audio message in response to a LINE event and confirms receipt.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Create an AudioSendMessage object with the audio URL and duration
        message = AudioSendMessage(
            original_content_url="https://6fa1-140-135-236-190.ngrok-free.app/static/mario.m4a",
            duration=20000
        )
        
        # Send the audio message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
        
        # Confirm receipt of the audio message
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Audio file has been sent successfully!'))
    except FileNotFoundError:
        # Log the specific exception for file not found
        print("Error: The audio file was not found.")
        
        # Send a specific error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="The audio file could not be found!"))
    except Exception as e:
        # Log the general exception for debugging purposes
        print(f"Error occurred: {e}")
        
        # Send a general error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while sending the audio!'))

    """Error log:
    Error occurred: LineBotApiError: status_code=400, 
    request_id=a6673403-86d3-4fb0-8c2c-e8c7427a7664,
      error_response={"details": [], "message": "Invalid reply token"}, 
      headers={'Server': 'legy', 'Content-Type': 'application/json', 
      'x-content-type-options': 'nosniff', 'x-frame-options': 'DENY', 
      'x-line-request-id': 'a6673403-86d3-4fb0-8c2c-e8c7427a7664', 
      'x-xss-protection': '1; mode=block', 'Content-Length': '33', 
      'Expires': 'Thu, 08 May 2025 09:21:45 GMT', 
      'Cache-Control': 'max-age=0, no-cache, no-store', 'Pragma': 'no-cache', 'Date': 
      'Thu, 08 May 2025 09:21:45 GMT', 'Connection': 'close'}
    語音播放時 顯示保存期限已過 無法播放
    """

def sendVideo(event):
    """
    Sends a video message in response to a LINE event.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Create a VideoSendMessage object with the video URL and preview image URL
        message = VideoSendMessage(
            original_content_url='https://6fa1-140-135-236-190.ngrok-free.app/static/robot.mp4',
            preview_image_url='https://6fa1-140-135-236-190.ngrok-free.app/static/robot.jpg'
        )
        
        # Send the video message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")
        
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while sending the video!'))

    """Error log:
    無法播放影片

    """


def sendButton(event):
    """
    Sends a button template message in response to a LINE event.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Create a TemplateSendMessage object with a ButtonsTemplate
        message = TemplateSendMessage(
            alt_text='按鈕樣板',
            template=ButtonsTemplate(
                thumbnail_image_url='https://assets.tmecosys.com/image/upload/t_web_rdp_recipe_584x480_1_5x/img/recipe/ras/Assets/2caca97b-77f6-48e7-837d-62642c0c9861/Derivates/12591894-e010-4a02-b04e-2627d8374298.jpg',  # Display image
                title='按鈕樣版示範',  # Main title
                text='請選擇:',  # Display text
                actions=[
                    MessageTemplateAction(
                        label='文字訊息',
                        text='@購買披薩'
                    ),
                    URITemplateAction(  # Open webpage
                        label='連結網頁',
                        uri='https://www.pizzahut.com.tw/'
                    ),
                    PostbackTemplateAction(  # Execute Postback function, trigger Postback event
                        label='回傳訊息',
                        data='action=buy'
                    )
                ]
            )
        )
        # Send the button template message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")
        
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while sending the button template!'))


def sendPizza(event):
    """
    Sends a text message confirming the purchase of a pizza in response to a LINE event.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Create a TextSendMessage object with the confirmation text
        message = TextSendMessage(
            text='感謝您購買披薩,我們將盡快為您製作。'
        )
        
        # Send the confirmation message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")
        
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while sending the pizza confirmation!'))

def sendBack_buy(event, backdata):
    """
    Handles the postback event for purchasing a pizza and sends a confirmation message.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    - backdata: A dictionary containing the postback data.
    """
    try:
        # Construct the confirmation message text
        text1 = '感謝您購買披薩,'
        text1 += '\n我們將盡快為您製作。'

        # Create a TextSendMessage object with the confirmation text
        message = TextSendMessage(text=text1)

        # Send the confirmation message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")

        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while processing your request.'))

def sendConfirm(event):
    """
    Sends a confirmation template message in response to a LINE event.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Create a TemplateSendMessage object with a ConfirmTemplate
        message = TemplateSendMessage(
            alt_text='Confirmation Template',
            template=ConfirmTemplate(
                text='你確定要購買此商品嗎?',
                actions=[
                    MessageTemplateAction(
                        label='Yes',
                        text='@yes'
                    ),
                    MessageTemplateAction(
                        label='No',
                        text='@no'
                    )
                ]
            )
        )
        
        # Send the confirmation template message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")
        
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while sending the confirmation template!'))

def sendYes(event):
    """
    Sends a confirmation message indicating a successful purchase.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Create a TextSendMessage object with the confirmation text
        message = TextSendMessage(
            text='感謝您的購買,\n我們將盡快寄出商品。'
        )
        
        # Send the confirmation message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")
        
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while processing your request.'))

def sendNo(event):
    """
    Sends a message indicating the cancellation of the operation.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Create a TextSendMessage object with the cancellation text
        message = TextSendMessage(
            text='沒關係,\n請您重新操作。'
        )
        
        # Send the cancellation message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")
        
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while processing your request.'))