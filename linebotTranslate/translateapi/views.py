from django.shortcuts import render

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, PostbackEvent, TextSendMessage
from linebot.models import QuickReply, QuickReplyButton, PostbackAction
from urllib.parse import parse_qsl

from translate import Translator
import variable_settings as varset

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

@csrf_exempt
def callback(request):
    # Check if the request method is POST
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')  # Decode the request body to UTF-8
        try:
            # Verify the signature and parse the body
            events = parser.parse(body, signature)  # Assuming 'parser' is defined to parse events

        except InvalidSignatureError:
            # Return forbidden response if the signature is invalid
            return HttpResponseForbidden()
        except LineBotApiError:
            # Return bad request response if there is an error with the Line Bot API
            return HttpResponseBadRequest()

        # Process each event in the events list
        for event in events:
            if isinstance(event, MessageEvent):
                userid, lang = readData(event)  # Read user ID and language settings
                mtext = event.message.text  # Get the text message from the event

                # Handle different commands based on the message text
                if mtext == '@使用說明':
                    showUse(event)  # Show usage instructions

                elif mtext == '@英文':
                    setLang(event, 'en', userid)  # Set language to English

                elif mtext == '@日文':
                    setLang(event, 'ja', userid)  # Set language to Japanese

                elif mtext == '@其他語文':
                    setElselang(event)  # Set other language options

                elif mtext == '@顯示設定':
                    showConfig(event, lang)  # Show current configuration

                else:  # General text translation
                    sendTranslate(event, lang, mtext)  # Translate the message

            elif isinstance(event, PostbackEvent):  # Handle postback events
                userid, lang = readData(event)  # Read user ID and language settings
                backdata = dict(parse_qsl(event.postback.data))  # Parse postback data
                sendData(event, backdata, userid)  # Send data back to the user

        return HttpResponse()  # Return a successful response

    else:
        return HttpResponseBadRequest()  # Return bad request response for non-POST methods
    

def readData(event):  # Read user ID and language settings
        # Extract user ID from the event
        userid = event.source.user_id  # Read user ID
        
        # Attempt to retrieve the user's language setting
        try:
            lang = varset.get(userid)  # Get the language setting for the user
            if lang is None:  # If no language is set, default to English
                raise ValueError("Language not set, defaulting to English.")
        except (KeyError, ValueError):  # Handle cases where user ID is not found or language is not set
            varset.set(userid, 'en')  # Set default language to English
            lang = 'en'  # Default language
        
        return userid, lang  # Return the user ID and language setting

def showUse(event):
    """Show usage instructions for the translation application."""
    try:
        # Prepare the usage instructions message
        instructions = (
            "1. 本應用程式可以將中文翻譯成多種語言。\n"
            "2. 預設翻譯語言為「英文」，預設發音為「關閉」。\n"
            "3. 按下「翻譯成英文」、「翻譯成日文」或「其他語言」來設定目標語言。\n"
            "4. 按下「顯示設定」以顯示當前翻譯語言以及是否要朗讀翻譯的文本。\n"
            "5. 輸入中文句子以進行翻譯。"
        )

        # Create a message to send back to the user
        message = TextSendMessage(text=instructions)

        # Send the message back to the user
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        # Log the error and send a generic error message
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='An error occurred.'))
        # Optionally, log the error details for debugging
        print(f"Error in showUse: {e}")

def setLang(event, language, userid):
    """Set the language preference for a user."""
    try:
        # Set the user's language preference
        varset.set(userid, language)
        
        # Prepare confirmation message based on language selected
        if language == 'en':
            message_text = "已設定翻譯語言為英文"
        elif language == 'ja':
            message_text = "已設定翻譯語言為日文"
        else:
            message_text = f"已設定翻譯語言為 {language}"
        
        # Send confirmation message
        message = TextSendMessage(text=message_text)
        line_bot_api.reply_message(event.reply_token, message)
        
    except Exception as e:
        # Handle errors and send error message
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='設定語言時發生錯誤'))
        print(f"Error in setLang: {e}")

def setElselang(event):
    """Show other language options using Quick Reply."""
    try:
        # Create quick reply buttons for other languages
        quick_reply_buttons = [
            QuickReplyButton(action=PostbackAction(label="法文", data="lang=fr")),
            QuickReplyButton(action=PostbackAction(label="德文", data="lang=de")),
            QuickReplyButton(action=PostbackAction(label="西班牙文", data="lang=es")),
            QuickReplyButton(action=PostbackAction(label="韓文", data="lang=ko")),
            QuickReplyButton(action=PostbackAction(label="泰文", data="lang=th")),
        ]
        
        # Create quick reply object
        quick_reply = QuickReply(items=quick_reply_buttons)
        
        # Send message with quick reply options
        message = TextSendMessage(text="請選擇要翻譯的語言：", quick_reply=quick_reply)
        line_bot_api.reply_message(event.reply_token, message)
        
    except Exception as e:
        # Handle errors and send error message
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='顯示語言選項時發生錯誤'))
        print(f"Error in setElselang: {e}")

def showConfig(event, lang):
    """Show current configuration settings."""
    try:
        # Map language codes to display names
        language_names = {
            'en': '英文',
            'ja': '日文',
            'fr': '法文',
            'de': '德文',
            'es': '西班牙文',
            'ko': '韓文',
            'th': '泰文'
        }
        
        # Get language display name
        lang_display = language_names.get(lang, lang)
        
        # Prepare configuration message
        config_text = f"目前設定：\n翻譯語言：{lang_display}"
        
        # Send configuration message
        message = TextSendMessage(text=config_text)
        line_bot_api.reply_message(event.reply_token, message)
        
    except Exception as e:
        # Handle errors and send error message
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='顯示設定時發生錯誤'))
        print(f"Error in showConfig: {e}")

def sendTranslate(event, target_lang, text):
    """Translate text and send the result."""
    try:
        # Create translator instance
        translator = Translator(to_lang=target_lang, from_lang='zh')
        
        # Perform translation
        translated_text = translator.translate(text)
        
        # Prepare response message
        response_text = f"{translated_text}"
        
        # Send translated message
        message = TextSendMessage(text=response_text)
        line_bot_api.reply_message(event.reply_token, message)
        
    except Exception as e:
        # Handle translation errors
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='翻譯時發生錯誤，請稍後再試'))
        print(f"Error in sendTranslate: {e}")

def sendData(event, backdata, userid):
    """Handle postback data from user interactions."""
    try:
        # Check if this is a language selection postback
        if 'lang' in backdata:
            language = backdata['lang']
            
            # Set the selected language
            varset.set(userid, language)
            
            # Map language codes to display names
            language_names = {
                'fr': '法文',
                'de': '德文', 
                'es': '西班牙文',
                'ko': '韓文',
                'th': '泰文'
            }
            
            # Get language display name
            lang_display = language_names.get(language, language)
            
            # Send confirmation message
            message_text = f"已設定翻譯語言為{lang_display}"
            message = TextSendMessage(text=message_text)
            line_bot_api.reply_message(event.reply_token, message)
            
    except Exception as e:
        # Handle errors and send error message
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='處理選項時發生錯誤'))
        print(f"Error in sendData: {e}")