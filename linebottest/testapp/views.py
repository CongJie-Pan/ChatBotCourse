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
from linebot.models import MessageEvent, TextSendMessage, TextMessage, ImageSendMessage, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction, AudioSendMessage, VideoSendMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction, URITemplateAction, PostbackTemplateAction, PostbackEvent, ConfirmTemplate, CarouselTemplate, CarouselColumn, ImageCarouselTemplate, ImageCarouselColumn, ImagemapSendMessage, BaseSize, MessageImagemapAction, ImagemapArea, URIImagemapAction, DatetimePickerTemplateAction, DatetimePickerAction

# Import Drink model
from .models import Drink

# Get http requests from "Treasury Invoice Information"
import requests

# Get xml.etree.ElementTree as ET for getting the data from "Treasury Invoice Information"
try:
    import xml.etree.ElementTree as ET
except ImportError:
    import xml.etree.cElementTree as ET


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
                elif mtext == '@菜單':
                    sendCarousel(event)
                elif mtext == '@圖片轉盤':
                    sendImgCarousel(event)
                elif mtext == '@購買披薩':
                    sendPizza(event)
                elif mtext == '@圖片地圖':
                    sendImgmap(event)
                elif mtext == '@日期時間':
                    sendDatetime(event)
                # Handle drink menu button selections
                elif mtext.endswith('介紹'):
                    drink_name = mtext.replace('介紹', '')
                    getDrinkDescription(event, drink_name)
                # Handle drink description requests with @ symbol (keeping for backward compatibility)
                elif mtext.startswith('@'):
                    drink_name = mtext[1:]  # Remove the @ prefix
                    getDrinkDescription(event, drink_name)
                elif mtext == '@飲料選單' or mtext == '@飲料' or mtext == '@飲料菜單':
                    sendDrinkMenuHelp(event)
                elif mtext == '@顯示本期中獎號碼':
                    showCurrent(event)
                elif mtext == '@顯示前期中獎號碼':
                    showOld(event)
                elif mtext == '@對獎':
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入發票最後三碼進行對獎'))
                elif len(mtext) == 3 and mtext.isdigit():
                    show3digit(event, mtext)
                else:
                    # Echo the received text message if no specific command is matched
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=mtext))


        if isinstance(event, PostbackEvent):  # Check if the event is a PostbackEvent
            backdata = dict(parse_qsl(event.postback.data))  # Parse the postback data into a dictionary
            
            if backdata.get('action') == 'buy':  # Check if the action is 'buy'
                sendBack_buy(event, backdata)  # Call the sendBack_buy function with the event and backdata
            
            elif backdata.get('action') == 'sell':  # Check if the action is 'sell'
                try:
                    sendData_sell(event, backdata)  # Call the sendData_sell function with the event and backdata
                except Exception as e:
                    print(f"Error occurred in sendData_sell: {e}")
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while processing your request!'))
            
            elif backdata.get('action') == 'return':  # Handle datetime picker postback
                handlePostback(event)  # Call the handlePostback function for datetime picker
                
            elif backdata.get('action') == 'drink_category':  # Handle drink category selection
                category = backdata.get('category')
                if category == 'tea':
                    sendTeaMenu(event)
                elif category == 'milk':
                    sendMilkMenu(event)
                elif category == 'other':
                    sendOtherMenu(event)

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

def sendCarousel(event):
    """
    Sends a carousel template message in response to a LINE event.
    Uses database to get drink information.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        print(f"[DEBUG] sendCarousel called, reply_token: {event.reply_token}")
        
        # Get drinks for each category (limit to 2 per category)
        tea_drinks = Drink.objects.filter(category='tea').order_by('id')[:2]
        milk_drinks = Drink.objects.filter(category='milk').order_by('id')[:2]
        other_drinks = Drink.objects.filter(category='other').order_by('id')[:2]
        
        print(f"[DEBUG] Retrieved drinks - Tea: {tea_drinks.count()}, Milk: {milk_drinks.count()}, Other: {other_drinks.count()}")
        
        # Create carousel columns
        columns = []
        
        # Add tea category if there are tea drinks
        if tea_drinks:
            print(f"[DEBUG] Creating tea column with drinks: {[d.name for d in tea_drinks]}")
            tea_actions = [
                PostbackTemplateAction(
                    label='查看茶類飲品',
                    data='action=drink_category&category=tea'
                )
            ]
            
            # Add buttons for tea drinks
            for drink in tea_drinks:
                tea_actions.append(
                    MessageTemplateAction(
                        label=drink.name,
                        text=f"{drink.name}介紹"
                    )
                )
            
            # Ensure only three actions maximum
            tea_actions = tea_actions[:3]
            
            # Add tea column
            tea_image_url = tea_drinks[0].image_url if tea_drinks[0].image_url else 'https://365dailydrinks.com/wp-content/uploads/2020/10/oolong-tea-project-1.jpg'
            print(f"[DEBUG] Tea column image URL: {tea_image_url}")
            
            columns.append(
                CarouselColumn(
                    thumbnail_image_url=tea_image_url,
                    title='茶類飲品',
                    text='經典烏龍茶系列',
                    actions=tea_actions
                )
            )
        
        # Add milk category if there are milk drinks
        if milk_drinks:
            print(f"[DEBUG] Creating milk column with drinks: {[d.name for d in milk_drinks]}")
            milk_actions = [
                PostbackTemplateAction(
                    label='查看奶類飲品',
                    data='action=drink_category&category=milk'
                )
            ]
            
            # Add buttons for milk drinks
            for drink in milk_drinks:
                milk_actions.append(
                    MessageTemplateAction(
                        label=drink.name,
                        text=f"{drink.name}介紹"
                    )
                )
            
            # Ensure only three actions maximum
            milk_actions = milk_actions[:3]
            
            # Add milk column
            milk_image_url = milk_drinks[0].image_url if milk_drinks[0].image_url else 'https://cc.tvbs.com.tw/img/program/upload/2024/07/04/20240704180750-6327e678.jpg'
            print(f"[DEBUG] Milk column image URL: {milk_image_url}")
            
            columns.append(
                CarouselColumn(
                    thumbnail_image_url=milk_image_url,
                    title='奶類飲品',
                    text='濃醇奶茶系列',
                    actions=milk_actions
                )
            )
        
        # Add other category if there are other drinks
        if other_drinks:
            print(f"[DEBUG] Creating other column with drinks: {[d.name for d in other_drinks]}")
            other_actions = [
                PostbackTemplateAction(
                    label='查看其他飲品',
                    data='action=drink_category&category=other'
                )
            ]
            
            # Add buttons for other drinks
            for drink in other_drinks:
                other_actions.append(
                    MessageTemplateAction(
                        label=drink.name,
                        text=f"{drink.name}介紹"
                    )
                )
            
            # Ensure only three actions maximum
            other_actions = other_actions[:3]
            
            # Add other column
            other_image_url = other_drinks[0].image_url if other_drinks[0].image_url else 'https://blog-cdn.roo.cash/blog/wp-content/uploads/2024/06/%E7%94%98%E8%94%97%E6%98%A5%E7%83%8F%E9%BE%8D.jpg'
            print(f"[DEBUG] Other column image URL: {other_image_url}")
            
            columns.append(
                CarouselColumn(
                    thumbnail_image_url=other_image_url,
                    title='其他飲品',
                    text='特調果茶系列',
                    actions=other_actions
                )
            )
        
        print(f"[DEBUG] Total columns created: {len(columns)}")
        
        # Create and send carousel message if we have any columns
        if columns:
            print(f"[DEBUG] Creating carousel template message...")
            message = TemplateSendMessage(
                alt_text='飲料菜單',
                template=CarouselTemplate(columns=columns)
            )
            print(f"[DEBUG] Sending carousel message...")
            line_bot_api.reply_message(event.reply_token, message)
            print(f"[DEBUG] Carousel message sent successfully")
        else:
            # Send a message if no drinks are available
            print(f"[DEBUG] No columns available, sending fallback message")
            message = TextSendMessage(text='目前沒有可用的飲品選項')
            line_bot_api.reply_message(event.reply_token, message)
            
    except Exception as e:
        # Log the error with full details
        print(f"[ERROR] Error occurred in sendCarousel: {e}")
        print(f"[ERROR] Error type: {type(e).__name__}")
        import traceback
        print(f"[ERROR] Full traceback:")
        traceback.print_exc()
        
        # Send error message
        try:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='傳送飲料菜單時發生錯誤!'))
        except Exception as reply_error:
            print(f"[ERROR] Failed to send error message: {reply_error}")

def sendImgCarousel(event):
    """
    Sends an image carousel message to the user using the LINE Bot API.
    The carousel contains images with actions that users can interact with.
    """
    try:
        # Create a template message with an image carousel
        message = TemplateSendMessage(
            alt_text='Image Carousel Template',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://i.imgur.com/4QfKuz1.png',
                        action=MessageTemplateAction(
                            label='Order Pizza',
                            text='Order Pizza'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://i.imgur.com/qaAdBkR.png',
                        action=MessageTemplateAction(
                            label='Order Drinks',
                            text='Order Drinks'
                        )
                    )
                ]
            )
        )

        # Send the carousel message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")

        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='圖片轉盤傳送失敗！'))

def sendImgmap(event):
    """
    Sends an imagemap message to the user using the LINE Bot API.
    The imagemap contains interactive areas that users can click on.
    """
    try:
        # Define the image URL and dimensions
        image_url = 'https://i.imgur.com/Yz2yzve.jpg'
        imgwidth = 1040  # The original image width must be 1040
        imgheight = 300

        # Create an ImagemapSendMessage object with the image and actions
        message = ImagemapSendMessage(
            base_url=image_url,
            alt_text="This is an imagemap",
            base_size=BaseSize(height=imgheight, width=imgwidth),
            actions=[
                # Define a message action for the left quarter of the image
                MessageImagemapAction(
                    text='You clicked the red area!',
                    area=ImagemapArea(
                        x=0,
                        y=0,
                        width=imgwidth * 0.25,
                        height=imgheight
                    )
                ),
                # Define a URI action for the right quarter of the image
                URIImagemapAction(
                    link_uri='https://im.cycu.edu.tw/',
                    area=ImagemapArea(
                        x=imgwidth * 0.75,
                        y=0,
                        width=imgwidth * 0.25,
                        height=imgheight
                    )
                )
            ]
        )

        # Send the imagemap message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")

        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while sending the imagemap!'))

def sendDatetime(event):
    """
    Sends a template message with datetime picker actions in response to a LINE event.
    When a date, time, or datetime is selected, it sends the selected value back to the user.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Create a TemplateSendMessage object with datetime picker actions
        message = TemplateSendMessage(
            alt_text='Datetime Picker Example',
            template=ButtonsTemplate(
                thumbnail_image_url='https://i.imgur.com/VxVB46z.jpg',
                title='Datetime Selection',
                text='Please select:',
                actions=[
                    DatetimePickerTemplateAction(
                        label="Select Date",
                        data="action=return&mode=date&label=Date",
                        mode="date",
                        initial="2021-06-01",
                        min="2021-01-01",
                        max="2021-12-31"
                    ),
                    DatetimePickerTemplateAction(
                        label="Select Time",
                        data="action=return&mode=time&label=Time",
                        mode="time",
                        initial="10:00",
                        min="00:00",
                        max="23:59"
                    ),
                    DatetimePickerTemplateAction(
                        label="Select Datetime",
                        data="action=return&mode=datetime&label=Datetime",
                        mode="datetime",
                        initial="2021-06-01T10:00",
                        min="2021-01-01T00:00",
                        max="2021-12-31T23:59"
                    )
                ]
            )
        )

        # Send the template message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred: {e}")

        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while sending the datetime picker!'))


def handlePostback(event):
    """
    Handles postback events from datetime picker actions and sends the selected value back to the user.

    Parameters:
    - event: The LINE event object containing the postback data.
    """
    try:
        # Parse the postback data into a dictionary
        backdata = dict(parse_qsl(event.postback.data))
        
        # Retrieve the mode and label from the postback data
        mode = backdata.get('mode')
        label = backdata.get('label')
        
        # Retrieve the selected value from the postback parameters
        selected_value = event.postback.params.get(mode)
        
        # Construct the response message
        response_message = f"Your {label}: {selected_value}"
        
        # Send the response message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response_message))
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error occurred in handlePostback: {e}")

        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred while processing your selection!'))

# Add new functions for handling drink menus
def sendTeaMenu(event):
    """
    Sends a tea menu with quick reply buttons in response to a LINE event.
    Uses database to get the tea drinks.
    """
    try:
        # 從資料庫獲取茶類飲品
        tea_drinks = Drink.objects.filter(category='tea')
        
        # 創建快速回覆按鈕
        buttons = []
        for drink in tea_drinks:
            buttons.append(
                QuickReplyButton(
                    action=MessageAction(label=drink.name, text=f"{drink.name}介紹")
                )
            )
        
        message = TextSendMessage(
            text='茶類 - 請選擇一項查看詳細介紹：',
            quick_reply=QuickReply(items=buttons)
        )
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        print(f"Error occurred: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='傳送茶類選單時發生錯誤!'))

def sendMilkMenu(event):
    """
    Sends a milk-based drink menu with quick reply buttons in response to a LINE event.
    Uses database to get the milk drinks.
    """
    try:
        # 從資料庫獲取奶類飲品
        milk_drinks = Drink.objects.filter(category='milk')
        
        # 創建快速回覆按鈕
        buttons = []
        for drink in milk_drinks:
            buttons.append(
                QuickReplyButton(
                    action=MessageAction(label=drink.name, text=f"{drink.name}介紹")
                )
            )
        
        message = TextSendMessage(
            text='奶類 - 請選擇一項查看詳細介紹：',
            quick_reply=QuickReply(items=buttons)
        )
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        print(f"Error occurred: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='傳送奶類選單時發生錯誤!'))

def sendOtherMenu(event):
    """
    Sends a menu of other drinks with quick reply buttons in response to a LINE event.
    Uses database to get the other drinks.
    """
    try:
        # 從資料庫獲取其他飲品
        other_drinks = Drink.objects.filter(category='other')
        
        # 創建快速回覆按鈕
        buttons = []
        for drink in other_drinks:
            buttons.append(
                QuickReplyButton(
                    action=MessageAction(label=drink.name, text=f"{drink.name}介紹")
                )
            )
        
        message = TextSendMessage(
            text='其他 - 請選擇一項查看詳細介紹：',
            quick_reply=QuickReply(items=buttons)
        )
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        print(f"Error occurred: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='傳送其他選單時發生錯誤!'))

def getDrinkDescription(event, drink_name):
    """
    Sends a description and image of a specific drink in response to a LINE event.
    Gets drink information from the database.
    
    Parameters:
    - event: The LINE event object containing the reply token and message details.
    - drink_name: The name of the drink to describe.
    """
    try:
        # 從資料庫獲取飲料資訊
        try:
            drink = Drink.objects.get(name=drink_name)
            messages = []
            
            # 如果有圖片網址，添加圖片訊息
            if drink.image_url:
                messages.append(
                    ImageSendMessage(
                        original_content_url=drink.image_url,
                        preview_image_url=drink.image_url
                    )
                )
            
            # 添加描述文字訊息
            messages.append(
                TextSendMessage(text=f'{drink.name}：{drink.description}')
            )
            
            # 發送多重訊息
            line_bot_api.reply_message(event.reply_token, messages)
            
        except Drink.DoesNotExist:
            # 如果找不到精確匹配，嘗試部分匹配
            try:
                drink = Drink.objects.filter(name__contains=drink_name).first()
                if drink:
                    messages = []
                    
                    # 如果有圖片網址，添加圖片訊息
                    if drink.image_url:
                        messages.append(
                            ImageSendMessage(
                                original_content_url=drink.image_url,
                                preview_image_url=drink.image_url
                            )
                        )
                    
                    # 添加描述文字訊息
                    messages.append(
                        TextSendMessage(text=f'{drink.name}：{drink.description}')
                    )
                    
                    # 發送多重訊息
                    line_bot_api.reply_message(event.reply_token, messages)
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f'抱歉，沒有找到 {drink_name} 的資訊。')
                    )
            except Exception:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f'抱歉，沒有找到 {drink_name} 的資訊。')
                )
    except Exception as e:
        # 記錄異常
        print(f"Error occurred: {e}")
        
        # 發送錯誤訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'傳送 {drink_name} 的資訊時發生錯誤!')
        )

def sendDrinkMenuHelp(event):
    """
    Sends help information about the drink menu system.
    Uses database to get available drink categories and counts.
    """
    try:
        # 獲取各類別飲品數量
        tea_count = Drink.objects.filter(category='tea').count()
        milk_count = Drink.objects.filter(category='milk').count()
        other_count = Drink.objects.filter(category='other').count()
        
        # 獲取各類別飲品名稱列表
        tea_drinks = Drink.objects.filter(category='tea').values_list('name', flat=True)
        milk_drinks = Drink.objects.filter(category='milk').values_list('name', flat=True)
        other_drinks = Drink.objects.filter(category='other').values_list('name', flat=True)
        
        help_text = "飲料點餐系統使用說明：\n\n"
        help_text += "1. 輸入「@菜單」查看主要飲料分類\n"
        help_text += "2. 選擇「茶類」、「奶類」或「其他」類別查看飲品選單\n"
        help_text += "3. 點選您想了解的飲品，系統將自動顯示詳細介紹\n\n"
        help_text += "可用命令：\n"
        help_text += "- @菜單：顯示飲料分類\n"
        help_text += "- @飲料選單：顯示此幫助信息\n\n"
        
        if tea_count > 0:
            help_text += f"茶類飲品({tea_count}種)：\n{', '.join(tea_drinks)}\n\n"
        
        if milk_count > 0:
            help_text += f"奶類飲品({milk_count}種)：\n{', '.join(milk_drinks)}\n\n"
        
        if other_count > 0:
            help_text += f"其他飲品({other_count}種)：\n{', '.join(other_drinks)}"
        
        message = TextSendMessage(text=help_text)
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        print(f"Error occurred: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='傳送飲料選單幫助時發生錯誤!'))

def showCurrent(event):
    """
    Fetches the current winning invoice numbers from the external service and sends them to the user.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Add timeout and headers for better reliability
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the XML content from the specified URL with timeout
        response = requests.get('https://invoice.etax.nat.gov.tw/invoice.xml', 
                               headers=headers, 
                               timeout=10)
        
        # Check if the response is successful
        if response.status_code != 200:
            print(f"HTTP Error: {response.status_code}")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text=f'發票 API 回應錯誤，狀態碼：{response.status_code}'))
            return
        
        # Check if response content is not empty
        if not response.text.strip():
            print("Empty response received")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text='發票 API 回應內容為空'))
            return
        
        # Log response for debugging
        print(f"Response received, length: {len(response.text)}")
        print(f"First 200 chars: {response.text[:200]}")
        
        # Parse the XML content to extract relevant information
        try:
            tree = ET.fromstring(response.text)
        except ET.ParseError as parse_error:
            print(f"XML Parse Error: {parse_error}")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text='發票資料 XML 格式解析錯誤'))
            return
        
        # Retrieve item tags
        items = list(tree.iter(tag='item'))
        
        if not items:
            print("No items found in XML")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text='發票 XML 中沒有找到任何項目'))
            return
        
        print(f"Found {len(items)} items in XML")
        
        # Check if the first item has enough elements
        if len(items[0]) < 4:
            print(f"First item has only {len(items[0])} elements")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text='發票資料格式不完整'))
            return
        
        # Extract the period and winning numbers from the first item
        title_element = items[0][0]
        ptext_element = items[0][3]
        
        if title_element is None or title_element.text is None:
            print("Title element is None or has no text")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text='無法取得發票期數資訊'))
            return
            
        if ptext_element is None or ptext_element.text is None:
            print("Winning numbers element is None or has no text")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text='無法取得中獎號碼資訊'))
            return
        
        title = title_element.text  # Period
        ptext = ptext_element.text  # Winning numbers
        
        print(f"Title: {title}")
        print(f"Winning numbers (first 100 chars): {ptext[:100]}")
        
        # Clean up the winning numbers text
        ptext = ptext.replace('<p>', '').replace('</p>', '\n')
        
        # Prepare the message to be sent
        message = title + '月\n' + ptext[:-1]  # Remove the last newline character
        
        # Check if message is too long for LINE (limit is 2000 characters)
        if len(message) > 2000:
            message = message[:1950] + '\n...(資訊過長，已截斷)'
        
        # Send the message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
        
    except requests.exceptions.ConnectTimeout:
        print("Connection timeout error")
        line_bot_api.reply_message(event.reply_token, 
            TextSendMessage(text='連線發票 API 超時，請稍後再試'))
    except requests.exceptions.ConnectionError:
        print("Connection error")
        line_bot_api.reply_message(event.reply_token, 
            TextSendMessage(text='無法連線到發票 API，請檢查網路連線'))
    except requests.exceptions.RequestException as req_error:
        print(f"Request error: {req_error}")
        line_bot_api.reply_message(event.reply_token, 
            TextSendMessage(text='發票 API 請求失敗'))
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Unexpected error occurred: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Send an error message back to the user with more specific information
        line_bot_api.reply_message(event.reply_token, 
            TextSendMessage(text='抱歉，沒有找到本期中獎號碼的資訊。請稍後再試。'))

def showOld(event):
    """
    Fetches the previous winning invoice numbers from the external service and sends them to the user.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    """
    try:
        # Add timeout and headers for better reliability
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the XML content from the specified URL with timeout
        response = requests.get('https://invoice.etax.nat.gov.tw/invoice.xml', 
                               headers=headers, 
                               timeout=10)
        
        # Check if the response is successful
        if response.status_code != 200:
            print(f"HTTP Error: {response.status_code}")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text=f'發票 API 回應錯誤，狀態碼：{response.status_code}'))
            return
        
        # Check if response content is not empty
        if not response.text.strip():
            print("Empty response received")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text='發票 API 回應內容為空'))
            return
        
        # Parse the XML content to extract relevant information
        try:
            tree = ET.fromstring(response.text)
        except ET.ParseError as parse_error:
            print(f"XML Parse Error: {parse_error}")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text='發票資料 XML 格式解析錯誤'))
            return
        
        # Retrieve item tags
        items = list(tree.iter(tag='item'))
        
        if not items:
            print("No items found in XML")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text='發票 XML 中沒有找到任何項目'))
            return
        
        # Check if we have at least 3 items for previous periods
        if len(items) < 3:
            print(f"Not enough items for previous periods, found: {len(items)}")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text='發票歷史資料不足'))
            return
        
        # Initialize the message string
        message = ""
        
        # Loop through the second and third items to extract title and winning numbers
        for i in range(1, 3):
            # Check if the item has enough elements
            if len(items[i]) < 4:
                print(f"Item {i} has only {len(items[i])} elements")
                continue
                
            title_element = items[i][0]
            ptext_element = items[i][3]
            
            if title_element is None or title_element.text is None:
                print(f"Title element for item {i} is None or has no text")
                continue
                
            if ptext_element is None or ptext_element.text is None:
                print(f"Winning numbers element for item {i} is None or has no text")
                continue
            
            title = title_element.text  # Period
            ptext = ptext_element.text  # Winning numbers
            
            # Clean up the winning numbers text
            ptext = ptext.replace('<p>', '').replace('</p>', '\n')
            
            # Append the title and winning numbers to the message
            message += f"{title}:\n{ptext}\n"
        
        # Check if we got any valid data
        if not message.strip():
            print("No valid previous period data found")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text='無法取得前期中獎號碼資訊'))
            return
        
        # Remove the last newline character for cleaner output
        message = message[:-1]
        
        # Check if message is too long for LINE (limit is 2000 characters)
        if len(message) > 2000:
            message = message[:1950] + '\n...(資訊過長，已截斷)'
        
        # Send the message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
        
    except requests.exceptions.ConnectTimeout:
        print("Connection timeout error")
        line_bot_api.reply_message(event.reply_token, 
            TextSendMessage(text='連線發票 API 超時，請稍後再試'))
    except requests.exceptions.ConnectionError:
        print("Connection error")
        line_bot_api.reply_message(event.reply_token, 
            TextSendMessage(text='無法連線到發票 API，請檢查網路連線'))
    except requests.exceptions.RequestException as req_error:
        print(f"Request error: {req_error}")
        line_bot_api.reply_message(event.reply_token, 
            TextSendMessage(text='發票 API 請求失敗'))
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Unexpected error occurred in showOld: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, 
            TextSendMessage(text='抱歉，沒有找到前期中獎號碼的資訊。請稍後再試。'))

def show3digit(event, mtext):
    """
    Fetches the winning invoice numbers from the external service and checks if the provided
    invoice number matches any winning numbers.

    Parameters:
    - event: The LINE event object containing the reply token and message details.
    - mtext: The invoice number input by the user.
    """
    try:
        # Add timeout and headers for better reliability
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the XML content from the specified URL with timeout
        response = requests.get('https://invoice.etax.nat.gov.tw/invoice.xml', 
                               headers=headers, 
                               timeout=10)
        
        # Check if the response is successful
        if response.status_code != 200:
            print(f"HTTP Error: {response.status_code}")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text=f'發票 API 回應錯誤，狀態碼：{response.status_code}'))
            return
        
        # Check if response content is not empty
        if not response.text.strip():
            print("Empty response received")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text='發票 API 回應內容為空'))
            return
        
        # Parse the XML content to extract relevant information
        try:
            tree = ET.fromstring(response.text)
        except ET.ParseError as parse_error:
            print(f"XML Parse Error: {parse_error}")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text='發票資料 XML 格式解析錯誤'))
            return
        
        # Retrieve item tags
        items = list(tree.iter(tag='item'))
        
        if not items:
            print("No items found in XML")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text='發票 XML 中沒有找到任何項目'))
            return
        
        # Check if the first item has enough elements
        if len(items[0]) < 4:
            print(f"First item has only {len(items[0])} elements")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text='發票資料格式不完整'))
            return
        
        # Extract winning numbers from the first item
        ptext_element = items[0][3]
        
        if ptext_element is None or ptext_element.text is None:
            print("Winning numbers element is None or has no text")
            line_bot_api.reply_message(event.reply_token, 
                TextSendMessage(text='無法取得中獎號碼資訊'))
            return
        
        ptext = ptext_element.text  # Winning numbers
        
        # Clean up the winning numbers text
        ptext = ptext.replace('<p>', '').replace('</p>', '\n').strip()
        
        print(f"Input: {mtext}")
        print(f"Winning numbers text: {ptext}")
        
        # Initialize lists for prize numbers
        prizelist = []  # Special prize or grand prize last three digits
        first_prizes = []  # First prize (頭獎) numbers
        
        # Parse the new format: 特別獎：64557267 特獎：64808075 頭獎：04322277、07903676、98883497
        lines = ptext.split('\n')
        prize_text = ' '.join(lines).strip()
        
        # Extract special prize
        if '特別獎：' in prize_text:
            special_start = prize_text.find('特別獎：') + 3
            special_end = prize_text.find(' ', special_start)
            if special_end == -1:
                special_end = len(prize_text)
            special_prize = prize_text[special_start:special_end].strip()
            if len(special_prize) >= 3:
                prizelist.append(special_prize[-3:])  # Last 3 digits
                print(f"Special prize: {special_prize}, last 3 digits: {special_prize[-3:]}")
        
        # Extract grand prize
        if '特獎：' in prize_text:
            grand_start = prize_text.find('特獎：') + 3
            grand_end = prize_text.find(' ', grand_start)
            if grand_end == -1:
                grand_end = len(prize_text)
            grand_prize = prize_text[grand_start:grand_end].strip()
            if len(grand_prize) >= 3:
                prizelist.append(grand_prize[-3:])  # Last 3 digits
                print(f"Grand prize: {grand_prize}, last 3 digits: {grand_prize[-3:]}")
        
        # Extract first prizes (頭獎)
        if '頭獎：' in prize_text:
            first_start = prize_text.find('頭獎：') + 3
            first_part = prize_text[first_start:].strip()
            # Split by commas or 、
            first_numbers = [num.strip() for num in first_part.replace('、', ',').split(',') if num.strip()]
            for num in first_numbers:
                if len(num) >= 3:
                    first_prizes.append(num[-3:])  # Last 3 digits
            print(f"First prizes: {first_numbers}, last 3 digits: {first_prizes}")
        
        print(f"Special/Grand prizes last 3 digits: {prizelist}")
        print(f"First prizes last 3 digits: {first_prizes}")
        
        # Check if the provided invoice number matches any winning numbers
        if mtext in prizelist:
            message = '符合特別獎或特獎後三碼!'
        elif mtext in first_prizes:
            message = '恭喜!符合頭獎後三碼,至少中六獎!'
        else:
            message = '很可惜,未中獎。請輸入下一張發票最後三碼。'
        
        # Send the response message using the LINE Bot API
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
        
    except requests.exceptions.ConnectTimeout:
        print("Connection timeout error")
        line_bot_api.reply_message(event.reply_token, 
            TextSendMessage(text='連線發票 API 超時，請稍後再試'))
    except requests.exceptions.ConnectionError:
        print("Connection error")
        line_bot_api.reply_message(event.reply_token, 
            TextSendMessage(text='無法連線到發票 API，請檢查網路連線'))
    except requests.exceptions.RequestException as req_error:
        print(f"Request error: {req_error}")
        line_bot_api.reply_message(event.reply_token, 
            TextSendMessage(text='發票 API 請求失敗'))
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Unexpected error occurred in show3digit: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Send an error message back to the user
        line_bot_api.reply_message(event.reply_token, 
            TextSendMessage(text='抱歉，對獎功能暫時無法使用。請稍後再試。'))