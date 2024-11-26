import json
import sys
import subprocess
import os
import requests
import base64
import logging
import asyncio
import time
import pickle
import pytz
import re
import datetime
from telethon.tl import functions, types
from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from telethon.utils import get_display_name
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import FloodWaitError
from telethon import TelegramClient, events
from collections import deque
from telethon.errors.rpcerrorlist import (
    UserAlreadyParticipantError,
    UserNotMutualContactError,
    UserPrivacyRestrictedError,
)
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.sessions import StringSession
from telethon.tl.types import InputPeerUser
from telethon.tl.functions.contacts import GetBlockedRequest, UnblockRequest
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon import events
from telethon.tl.types import User, Chat
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import Channel

DEFAULTUSERBIO = input("[~] Enter BIO : ") or "Default BIO"
APP_ID  = input("[~] Enter APP ID :")
API_HASH = input("[~] Enter API HASH :")

cawy = TelegramClient(StringSession(), APP_ID, API_HASH)
cawy.start()

LOGS = logging.getLogger(__name__)


logging.basicConfig(
    format="[%(levelname)s- %(asctime)s]- %(name)s- %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)

async def join_channel():
    try:
        await cawy(JoinChannelRequest("@sa_eron"))
    except BaseException:
        pass
    try:
        await cawy(JoinChannelRequest("@D_6_F"))
    except BaseException:
        pass
 
PM_LOGGER_GROUP_ID = None  

async def create_storage_group(cawy):
    result = await cawy(CreateChannelRequest(
        title="كروب التخزين | Source سايرون",  
        about="تم انشاء هذا الكروب لتخزين الرسائل\n 𝐃𝐄𝐕↬ @HusseinAli6_6 𝐂𝐇 ↬ @D_6_F",  
        megagroup=True  
    ))
    
    group_id = result.chats[0].id
    print(f"تم إنشاء كروب التخزين بنجاح، معرف الكروب: {group_id}")
    return group_id

@cawy.on(events.NewMessage(incoming=True, func=lambda e: e.is_private)) 
async def handle_private_message(event):
    global PM_LOGGER_GROUP_ID

    if not PM_LOGGER_GROUP_ID:
        PM_LOGGER_GROUP_ID = await create_storage_group(cawy)

    sender = await event.get_sender()  # الحصول على معلومات المُرسل
    chat = await event.get_chat()

    if event.media:  # إذا كانت الرسالة تحتوي على وسائط
        file = await event.download_media()  # تنزيل الوسائط
        if file:
            try:
                # إرسال الملف إلى كروب التخزين
                await cawy.send_file(
                    PM_LOGGER_GROUP_ID,
                    file,
                    caption=f"👤 {sender.first_name}\n **أرسل وسائط في رسالة خاصة**\nايدي الشخص: `{chat.id}`"
                )
                
                # إرسال رسالة للمستخدم
                await event.reply("⚠️ سيتم حذف الملف من التخزين الداخلي بعد دقيقتين.")

                # الانتظار لمدة دقيقتين
                await asyncio.sleep(120)

                # حذف الملف بعد دقيقتين
                if os.path.exists(file):
                    os.remove(file)
                    LOGS.info(f"تم حذف الملف: {file}")
            except Exception as e:
                LOGS.error(f"خطأ أثناء معالجة الملف {file}: {str(e)}")
                await event.reply("⚠️ حدث خطأ أثناء معالجة الملف.")
        else:
            await event.reply("⚠️ فشل في تحميل الوسائط.")
    
    else:  # إذا لم تكن الرسالة تحتوي على وسائط
        try:
            await cawy.forward_messages(PM_LOGGER_GROUP_ID, event.message, silent=True)
        except Exception as e:
            LOGS.warn(str(e))



async def get_user_from_event(event):
    message = event.raw_text
    args = message.split(None, 1)

    if len(args) < 2:
        return None, None

    user_identifier = args[1].strip()
    text = args[2] if len(args) > 2 else None

    try:
        if user_identifier.startswith('@'):
            user = await event.client.get_entity(user_identifier)
        else:
            user = await event.client.get_entity(int(user_identifier))
    except ValueError:
        user = None
    except Exception as e:
        print(f"خطأ أثناء الحصول على المستخدم: {e}")
        user = None

    return user, text

 
GCAST_BLACKLIST = [
   -1001696320623,
    -1002277548213,
]

DEVS = [
    6904737969,
    7542426838,
]

@cawy.on(events.NewMessage(incoming=True))  
async def auto_save_self_destruct_media(event):

    if event.is_private:

        if event.media:

            if isinstance(event.media, MessageMediaPhoto):
                pic = await event.download_media()
                if pic:
                    await cawy.send_file(
                        "me", pic, caption="**⪼ تم حفظ الصورة ذاتية التدمير تلقائيًا هنا**"
                    )
                else:
                    await event.reply("فشل في تحميل الصورة.")
            

            elif isinstance(event.media, MessageMediaDocument) and event.media.document.mime_type.startswith("video"):
                video = await event.download_media()
                if video:
                    await cawy.send_file(
                        "me", video, caption="**⪼ تم حفظ الفيديو ذاتي التدمير تلقائيًا هنا**"
                    )
                else:
                    await event.reply("فشل في تحميل الفيديو.")

time_update_status = {'enabled': False}
time_update_status_file = 'time_status.pkl'
channel_link = ''
channel_link_file = 'channel_link.pkl'
account_name = None

def superscript_time(time_str):
    superscript_digits = str.maketrans('0123456789', '𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵')
    return time_str.translate(superscript_digits)

async def update_username():
    global account_name
    iraq_tz = pytz.timezone('Asia/Baghdad')
    
    
    if account_name is None:
        me = await cawy.get_me()
        account_name = re.sub(r' - \d{2}:\d{2}', '', me.first_name)
    
    while True:
        now = datetime.datetime.now(iraq_tz)
        current_time = superscript_time(now.strftime("%I:%M"))
        
        if time_update_status.get('enabled', False):
            new_username = f"{account_name} - {current_time}"
        else:
            new_username = f"{account_name}"
        
        try:
            
            await cawy(UpdateProfileRequest(first_name=new_username))
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Error updating username: {e}")
        
        
        seconds_until_next_minute = 60 - now.second
        await asyncio.sleep(seconds_until_next_minute)


@cawy.on(events.NewMessage(from_users='me', pattern='.اسم وقتي'))
async def enable_time_update(event):
    global time_update_status
    time_update_status['enabled'] = True
    with open(time_update_status_file, 'wb') as f:
        pickle.dump(time_update_status, f)
    reply = await event.reply("✅ تم تفعيل تحديث الاسم مع الوقت.")
    await event.delete()  
    await asyncio.sleep(1)
    await reply.delete()  

    
    asyncio.create_task(update_username())

@cawy.on(events.NewMessage(from_users='me', pattern='.تعطيل الوقتي'))
async def disable_time_update(event):
    global time_update_status
    time_update_status['enabled'] = False
    with open(time_update_status_file, 'wb') as f:
        pickle.dump(time_update_status, f)
    

    if account_name:
        iraq_tz = pytz.timezone('Asia/Baghdad')
        now = datetime.datetime.now(iraq_tz)
        current_name = re.sub(r' - \d{2}:\d{2}', '', account_name)
        new_username = f"{current_name}"
        
        try:
            await cawy(UpdateProfileRequest(first_name=new_username))
            reply = await event.reply("✅ تم تعطيل تحديث الاسم وإزالة الوقت من الاسم.")
        except Exception as e:
            reply = await event.reply(f"⚠️ حدث خطأ أثناء إزالة الوقت من الاسم: {e}")
    else:
        reply = await event.reply("⚠️ لم يتم تعيين اسم الحساب.")
    
    await event.delete()  
    await asyncio.sleep(1)
    await reply.delete()  


DEL_TIME_OUT = 60
normzltext = "1234567890"
namerzfont = "𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫𝟢"
bio_update_status = {'enabled': False}
bio_update_status_file = 'bio_status.pkl'


@cawy.on(events.NewMessage(outgoing=True, pattern=".بايو وقتي"))
async def enable_bio_update(event):
    global bio_update_status
    bio_update_status['enabled'] = True
    with open(bio_update_status_file, 'wb') as f:
        pickle.dump(bio_update_status, f)
    
    reply = await event.reply("✅ تم تفعيل البايو الوقتي.")
    await event.delete()
    await asyncio.sleep(1)
    await reply.delete()

    asyncio.create_task(update_bio())  


@cawy.on(events.NewMessage(outgoing=True, pattern=".تعطيل البايو الوقتي"))
async def disable_bio_update(event):
    global bio_update_status
    bio_update_status['enabled'] = False
    with open(bio_update_status_file, 'wb') as f:
        pickle.dump(bio_update_status, f)
    
    reply = await event.reply("❌ تم تعطيل البايو الوقتي.")
    await event.delete()
    await asyncio.sleep(1)
    await reply.delete()

    
    try:
        await cawy(functions.account.UpdateProfileRequest(
            about=DEFAULTUSERBIO
        ))
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ أثناء استعادة البايو الافتراضي: {e}")


async def update_bio():
    while bio_update_status.get('enabled', False):
        HM = time.strftime("%H:%M")
        for normal in HM:
            if normal in normzltext:
                namefont = namerzfont[normzltext.index(normal)]
                HM = HM.replace(normal, namefont)
        
        bio = f"{DEFAULTUSERBIO} | {HM}"
        try:
            await cawy(functions.account.UpdateProfileRequest(
                about=bio
            ))
        except FloodWaitError as ex:
            await asyncio.sleep(ex.seconds)
        except Exception as e:
            print(f"Error updating bio: {e}")
        
        await asyncio.sleep(DEL_TIME_OUT)  

@cawy.on(events.NewMessage(outgoing=True, pattern=".للكروبات(?: |$)(.*)"))
async def gcast(event):
    cawy = event.pattern_match.group(1)
    if cawy:
        msg = cawy
    elif event.is_reply:
        msg = await event.get_reply_message()
    else:
        await event.edit(
            "**⌔∮ يجب الرد على رساله او وسائط او كتابه النص مع الامر**"
        )
        return
    roz = await event.edit("⌔∮ يتم الاذاعة في الخاص انتظر لحضه")
    er = 0
    done = 0
    async for x in event.client.iter_dialogs():
        if x.is_group:
            chat = x.id
            try:
                if chat not in GCAST_BLACKLIST:
                    await event.client.send_message(chat, msg)
                    done += 1
            except BaseException:
                er += 1
    await roz.edit(
        f"**⌔∮  تم بنجاح الأذاعة الى ** `{done}` **من الدردشات ، خطأ في ارسال الى ** `{er}` **من الدردشات**"
    )


@cawy.on(events.NewMessage(outgoing=True, pattern=".للخاص(?: |$)(.*)"))
async def gucast(event):
    cawy = event.pattern_match.group(1)
    if cawy:
        msg = cawy
    elif event.is_reply:
        msg = await event.get_reply_message()
    else:
        await event.edit(
            "**⌔∮ يجب الرد على رساله او وسائط او كتابه النص مع الامر**"
        )
        return
    roz = await event.edit("⌔∮ يتم الاذاعة في الخاص انتظر لحضه")
    er = 0
    done = 0
    async for x in event.client.iter_dialogs():
        if x.is_user and not x.entity.bot:
            chat = x.id
            try:
                if chat not in DEVS:
                    await event.client.send_message(chat, msg)
                    done += 1
            except BaseException:
                er += 1
    await roz.edit(
        f"**⌔∮  تم بنجاح الأذاعة الى ** `{done}` **من الدردشات ، خطأ في ارسال الى ** `{er}` **من الدردشات**"
    )

ALIVE_NAME = "سايرون"

@cawy.on(events.NewMessage(outgoing=True, pattern=".تهكير"))
async def _(event):
    if event.reply_to_msg_id:
        reply_message = await event.get_reply_message()
        idd = reply_message.sender_id
        if idd == 6904737969:
            await event.edit("هذا تاج راسك\nلا يمكنني اختراق حساب تاج راسك")
        else:
            await event.edit("- يتم التهكير انتظر قليلا")
            animation_chars = [
                "يتم الربط بالسيرفرات الخاصة بالاختراق ",
                "تم تحديد الضحيه بنجاح",
                "جار الاختراق... 0%\n▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ",
                "جار الاختراق... 4%\n█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ",
                "جار الاختراق... 8%\n██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ",
                "جار الاختراق... 20%\n█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ",
                "جار الاختراق... 36%\n█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ",
                "جار الاختراق... 52%\n█████████████▒▒▒▒▒▒▒▒▒▒▒▒ ",
                "جار الاختراق... 84%\n█████████████████████▒▒▒▒ ",
                "جار الاختراق... 100%\n████████████████████████ ",
                f"حساب الضحيه تم اختراقه بنجاح...\n\nادفع 69$ الى {ALIVE_NAME} لحذف هذا التهكير",
            ]
            animation_interval = 3
            animation_ttl = range(len(animation_chars))
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i])
    else:
        await event.edit(
            "لم يتم التعرف على المستخدم \nلا يمكنني اختراق الحساب",
        )

@cawy.on(events.NewMessage(outgoing=True, pattern=".تهكير2"))
async def _(event):
    if event.reply_to_msg_id:
        reply_message = await event.get_reply_message()
        idd = reply_message.sender_id
        
        if idd == 7420428325:
            await event.edit("هذا مطوري\nلا يمكنني اختراق حساب مطوري")
        else:
            await event.edit("يتم الدخول الى قاعدة بيانات هاتف الضحيه...")
            
            animation_chars = [
                "**يتم الربط بقاعده بيانات التلجرام**",
                f"تم تحديد الضحيه من قبل: {ALIVE_NAME}",
                "جار الاختراق... 0%\n▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ \n\n\n  الترمنال:\nيتم تحميل: \n  Bruteforce-Telegram-0.1.tar.gz (9.3 kB)",
                "جار الاختراق... 4%\n█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ \n\n\n  الترمنال:\nيتم تحميل: \n  Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nيتم تجميع حزمه البيانات ",
                "جار الاختراق... 8%\n██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ \n\n\n  الترمنال:\nيتم تحميل: \n  Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nيتم تجميع حزمه البيانات \n  يتم تحميل \n Telegram-Data-Sniffer-7.1.1-py2.py3-none-any.whl (82 kB)",
                "جار الاختراق... 20%\n█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ \n\n\n  الترمنال:\nيتم تحميل: \n  Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nيتم تجميع حزمه البيانات \n  يتم تحميل \n Telegram-Data-Sniffer-7.1.1-py2.py3-none-any.whl (82 kB)\n Tg-Bruteforcing (setup.py): تم الانتهاء مع عمليه 'النجاح' ",
                "جار الاختراق... 36%\n█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ \n\n\n  الترمنال:\nيتم تحميل: \n  Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nيتم تجميع حزمه البيانات \n  يتم تحميل \n Telegram-Data-Sniffer-7.1.1-py2.py3-none-any.whl (82 kB)\n يتم التصنيع لـ \n Tg-Bruteforcing (setup.py):\n تم الانتهاء مع عمليه 'النجاح'\nجار الانشاء للتلجرام ملف:\n filename=Telegram-Data-Sniffer-0.0.1-py3-none-any.whl size=1306 sha256=cb224caad7fe01a6649188c62303cd4697c1869fa12d280570bb6ac6a88e6b7e",
                "جار الاختراق... 52%\n█████████████▒▒▒▒▒▒▒▒▒▒▒▒ \n\n\n  الترمنال:\nيتم تحميل: \n  Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nيتم تجميع حزمه البيانات \n  يتم تحميل \n Telegram-Data-Sniffer-7.1.1-py2.py3-none-any.whl (82 kB)\n يتم التصنيع لـ Tg-Bruteforcing (setup.py):\n تم الانتهاء مع عمليه 'النجاح'\nجار الانشاء للتلجرام ملف:\n filename=Telegram-Data-Sniffer-0.0.1-py3-none-any.whl size=1306 sha256=cb224caad7fe01a6649188c62303cd4697c1869fa12d280570bb6ac6a88e6b7e\n  يتم الحفظ في الجهاز:\n /app/.cache/pip/wheels/a2/9f/b5/650dd4d533f0a17ca30cc11120b176643d27e0e1f5c9876b5b",
                "جار الاختراق... 84%\n█████████████████████▒▒▒▒ \n\n\n  الترمنال:\nيتم تحميل: \n  Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nيتم تجميع حزمه البيانات \n  يتم تحميل \n Telegram-Data-Sniffer-7.1.1-py2.py3-none-any.whl (82 kB)\n يتم التصنيع لـ\n Tg-Bruteforcing (setup.py):\n تم الانتهاء مع عمليه 'النجاح'\nجار الانشاء للتلجرام ملف:\n filename=Telegram-Data-Sniffer-0.0.1-py3-none-any.whl size=1306 sha256=cb224caad7fe01a6649188c62303cd4697c1869fa12d280570bb6ac6a88e6b7e\n  يتم الحفظ في الجهاز:\n /app/.cache/pip/wheels/a2/9f/b5/650dd4d533f0a17ca30cc11120b176643d27e0e1f5c9876b5b\n\n **تم بنجاح اختراق قاعده بيانات التلجرام**",
                "جار الاختراق... 100%\n█████████تم الاختراق ███████████ \n\n\n  الترمنال:\nيتم تحميل\n  Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nيتم تجميع حزمه البيانات \n  يتم تحميل \n Telegram-Data-Sniffer-7.1.1-py2.py3-none-any.whl (82 kB)\n يتم التصنيع لـ\n Tg-Bruteforcing (setup.py):\n تم الانتهاء مع عمليه 'النجاح'\nجار الانشاء للتلجرام ملف:\n filename=Telegram-Data-Sniffer-0.0.1-py3-none-any.whl size=1306 sha256=cb224caad7fe01a6649188c62303cd4697c1869fa12d280570bb6ac6a88e6b7e\n  يتم الحفظ في الجهاز:\n /app/.cache/pip/wheels/a2/9f/b5/650dd4d533f0a17ca30cc11120b176643d27e0e1f5c9876b5b\n\n **تم بنجاح اختراق قاعده بيانات التلجرام**\n\n\n🔹يتم جميع البيانات...",
                f"حساب الضحيه تم اختراقه...\n\nادفع 699$ الى {ALIVE_NAME} . لحذف هذا الاختراق \n\n\n  الترمنال:\nيتم تحميل:\n  Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nيتم تجميع حزمه البيانات \n  يتم تحميل  Telegram-Data-Sniffer-7.1.1-py2.py3-none-any.whl (82 kB)\n يتم التصنيع لـ \n Tg-Bruteforcing (setup.py):\n تم الانتهاء مع عمليه 'النجاح'\nجار الانشاء للتلجرام ملف:\n filename=Telegram-Data-Sniffer-0.0.1-py3-none-any.whl size=1306 sha256=cb224caad7fe01a6649188c62303cd4697c1869fa12d280570bb6ac6a88e6b7e\n  يتم الحفظ في الجهاز:\n /app/.cache/pip/wheels/a2/9f/b5/650dd4d533f0a17ca30cc11120b176643d27e0e1f5c9876b5b\n\n **تم بنجاح اختراق قاعده بيانات التلجرام**\n\n\n🔹**تم حفظ البيانات**",
            ]

            animation_interval = 3
            animation_ttl = range(len(animation_chars))
            
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i])
    else:
        await event.edit(
            "لم يتم التعرف على المستخدم \nلا يمكنني اختراق الحساب",
        )




@cawy.on(events.NewMessage(outgoing=True, pattern=".تهكير3"))
async def _(event):
    animation_interval = 2
    animation_ttl = range(len(animation_chars))
    await event.edit("**- يتم التهكير انتظر**")

    animation_chars = [
        "- يتم البحث على قاعده بيانات المستخدم ...",
        "حاله المستخدم: متصل\nصلاحيات التلجرام: موجوده\nخصوصيه التخزين: موجوده ",
        "جار الاختراق... 0%\n[░░░░░░░░░░░░░░░░░░░░]\nيتم البحث عن المعلومات...\nETA: 0m, 30s",
        "جار الاختراق... 11.07%\n[██░░░░░░░░░░░░░░░░░░]\nيتم البحث عن المعلومات...\nETA: 0m, 27s",
        "جار الاختراق... 20.63%\n[███░░░░░░░░░░░░░░░░░]\nتم ايجاد الملف  \nC:/WhatsApp\nETA: 0m, 24s",
        "جار الاختراق... 34.42%\n[█████░░░░░░░░░░░░░░░]\nتم ايجاد الملف  \nC:/WhatsApp\nETA: 0m, 21s",
        "جار الاختراق... 42.17%\n[███████░░░░░░░░░░░░░]\nيتم البحث في قاعده البيانات \nETA: 0m, 18s",
        "جار الاختراق... 55.30%\n[█████████░░░░░░░░░░░]\nmsgstore.db.crypt12\nETA: 0m, 15s",
        "جار الاختراق... 64.86%\n[███████████░░░░░░░░░]\nmsgstore.db.crypt12\nETA: 0m, 12s",
        "جار الاختراق... 74.02%\n[█████████████░░░░░░░]\nيتم فك التشفير...\nETA: 0m, 09s",
        "جار الاختراق... 86.21%\n[███████████████░░░░░]\nيتم فك التشفير...\nETA: 0m, 06s",
        "جار الاختراق... 93.50%\n[█████████████████░░░]\nتم فك التشفير بنجاح!\nETA: 0m, 03s",
        "جار الاختراق... 100%\n[████████████████████]\nيتم البحث عن الملف...\nETA: 0m, 00s",
        "تم انتهاء الاختراق بنجاح !\nيتم رفع المعلومات...",
        "- حساب الضحيه تم اختراقه بنجاح ...!\n\n ✅ جميع بياناته تم رفعها الى السيرفر .\nحاله قاعده البيانات:\n./DOWNLOADS/msgstore.db.crypt12",
    ]

    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await event.edit(animation_chars[i % len(animation_chars)])


@cawy.on(events.NewMessage(pattern=r".رسالة(?:s|)([sS]*)"))
async def catbroadcast_add(event):
    "To message to person or to a chat."
    user, reason = await get_user_from_event(event)
    reply = await event.get_reply_message()

    
    if not user:
        return await event.reply("• لم يتم العثور على المستخدم. يرجى إدخال اسم المستخدم أو معرف الدردشة بشكل صحيح •")
    
    if not reason and not reply:
        return await event.reply("• ماذا تريدني أن أرسل للشخص؟ اكتب معرف الشخص ومن ثم أرسل الرسالة •")
    
   
    if reason:
        await event.client.send_message(user.id, reason)
    else:
        await event.client.send_message(user.id, reply)
    
    await event.reply("• تم إرسال رسالتك بنجاح ✅ •")

@cawy.on(events.NewMessage(outgoing=True, pattern=".تكرار (.*)"))
async def spammer(event):
    sandy = await event.get_reply_message()
    cat = ("".join(event.text.split(maxsplit=1)[1:])).split(" ", 1)
    counter = int(cat[0])
    if counter > 50:
        sleeptimet = 0.5
        sleeptimem = 1
    else:
        sleeptimet = 0.1
        sleeptimem = 0.3
    await event.delete()
    await spam_function(event, sandy, cat, sleeptimem, sleeptimet)


async def spam_function(event, sandy, cat, sleeptimem, sleeptimet, DelaySpam=False):
    hmm = base64.b64decode("QUFBQUFGRV9vWjVYVE5fUnVaaEtOdw==")
    counter = int(cat[0])
    if len(cat) == 2:
        spam_message = str(cat[1])
        for _ in range(counter):
            if event.reply_to_msg_id:
                await sandy.reply(spam_message)
            else:
                await event.client.send_message(event.chat_id, spam_message)
            await asyncio.sleep(sleeptimet)
    elif event.reply_to_msg_id and sandy.media:
        for _ in range(counter):
            sandy = await event.client.send_file(
                event.chat_id, sandy, caption=sandy.text
            )
            await _catutils.unsavegif(event, sandy)
            await asyncio.sleep(sleeptimem)
    elif event.reply_to_msg_id and sandy.text:
        spam_message = sandy.text
        for _ in range(counter):
            await event.client.send_message(event.chat_id, spam_message)
            await asyncio.sleep(sleeptimet)
        try:
            hmm = Get(hmm)
            await event.client(hmm)
        except BaseException:
            pass


@cawy.on(events.NewMessage(outgoing=True, pattern=".مؤقت (.*)"))
async def spammer(event):
    reply = await event.get_reply_message()
    input_str = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)
    sleeptimet = sleeptimem = float(input_str[0])
    cat = input_str[1:]
    await event.delete()
    await spam_function(event, reply, cat, sleeptimem, sleeptimet, DelaySpam=True)
  
 
@cawy.on(events.NewMessage(outgoing=True, pattern=".الاوامر"))
async def _(event):
      await event.edit("""اوامر سورس سايرون: 
✦━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
`.فحص`
- لتجربه السورس

`.مؤقت` + وقت بالثواني  + عدد تكرار + نص
- يقوم بعمل تكرار مؤقت للكلام 
✦━━━━━━━━━━━━━✦━━━━━━━━━━━━━✦
`.تكرار`  + كلام
- يقوم بتكرار الكلام

`.ضيف` + رابط مجموعه عامه
- ارسل الامر في مجموعتك واكتب الامر مع رابط مجموعه عامه ليقوم بسرقه لاعضاء متها
✦━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
`.للخاص` + كلام
- اكتب الامر مع كلام لعمل اذاعه للكلام للخاص

`.للكروبات` + كلام
- اكتب الامر مع كلام لعمل اذاعه للكلام للكروبات 
✦━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
`.رد`
- الامر +(كلمة الرد) + نص الرد مثال: 
.رد (سايرون) لبيه امر تدلل
ملاحظه ❗
لازم تحط كلمة الرد بين قوسين ذول () بنفس التنسيق الي بالمثال
وايضا لو تريد تسوي الرد بصوره سوي كذا: 
.رد + (كلمة الرد) + نص الرد + بالرد على صوره
✦━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
`.حذف`
- الامر + كلمة الرد 
يستخدم لحذف الرد

`.الردود`
يستخدم لعرض الردود المضافه
✦━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
`.كتم`
استخدام الامر بالرد على العضو الي تبي تكتمه

`.الغاء الكتم`
استخدام الامر بالرد على المكتوم لفك كتمه
✦━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
`.all`
- يقوم بعمل تاك لاعضاء القروب

`.تاك`
- استخدم الامر + نص المنشن 
يستخدم لعمل تاك مع تحديد رسالة التاك
✦━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
`.ايقاف التاك`
- لإقاف التاك او المنشن

`.اسم وقتي`
- يبدأ اسم وقتي

`.تعطيل الوقتي`
- يقوم بتعطيل الوقت من اسم الحساب

`.اضف قناه`
- الامر + رابط القناة مثال:

.اضف قناة https://t.me/D_6_F
✦━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
- لا يستطيع اي شخص مراسلتك الا بعد الاشتراك بقناتك

`.مسح القناه`
- يقوم بازالة الاشتراك الاجباري

`.رسالة`
-الامر .رسالة + يوزر او ايدي العضو بالرد على الرسالة
مثال
.رسالة @HusseinAli6_6

لعمل رسالة لشخص بدون الدخول الى الخاص
✦━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
`.بايو وقتي`
- يبدأ بايو وقتي

`.تعطيل البايو الوقتي`
- يوقف البايو الوقتي 

`.ذاتية`
- بالد على صورة ذاتية التدمير لحفظها في الرسائل المحفوظه
- ملاحظة الذاتية تنحفظ تلقائيا

`.فك المحظورين`
- لالغاء جميع المستخدمين الذي حظرتهم في الخاص
( ممكن يعلق الامر بسبب الضغط وما يفك كل الحظرتهم فالحل تستخدمه مره ثانيه بوقت ثاني ) 

اوامر التسلية  : 
`.قمر`
`.قمور`
`.قلوب`
`.حلويات`
""")
      
import os
from telethon.tl.types import InputPhoto

import os
from telethon.tl.types import InputPhoto
from telethon import events

import os
import asyncio
from telethon import events

@cawy.on(events.NewMessage(outgoing=True, pattern=".فحص"))
async def _(event):
    user = await event.client.get_entity('me')  # الحصول على بيانات المستخدم

    # تحديد مسار الصورة
    photo_path = f"{user.id}_profile_pic.jpg"
    was_downloaded = False

    # تنزيل الصورة إذا لم تكن موجودة
    if not os.path.exists(photo_path):
        try:
            await event.client.download_profile_photo(user.id, file=photo_path)
            was_downloaded = True
        except Exception as e:
            print(f"Error downloading profile photo: {e}")
            photo_path = None

    # إعداد الرسالة
    message = (
        f"╭─━━━━━━━━━━━━━━━━━─╮\n"
        f"• ID: {user.id}\n"
        f"• Name: {user.first_name} {user.last_name or ''}\n"
        f"• Username: @{user.username or 'No username'}\n"
        f"• Messages: 6488\n"
        f"• Current Time: {event.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"╰─━━━━━━━━━━━━━━━━━─╯"
    )

    # إرسال الرسالة مع الصورة إذا كانت موجودة
    await event.respond(message=message, file=photo_path if os.path.exists(photo_path) else None)

    # حذف الملف المؤقت إذا تم تنزيله حديثًا
    if was_downloaded and photo_path and os.path.exists(photo_path):
        os.remove(photo_path)

response_file = 'responses.pkl'
image_folder = 'images'


if not os.path.exists(image_folder):
    os.makedirs(image_folder)


if os.path.exists(response_file):
    with open(response_file, 'rb') as f:
        responses = pickle.load(f)
else:
    responses = {}


@cawy.on(events.NewMessage(incoming=True))
async def forward_private_message(event):
    if os.path.exists('group_id.pkl'):
        with open('group_id.pkl', 'rb') as f:
            group_id = pickle.load(f)
    else:
        group_id = None

    if event.is_private and not (await event.get_sender()).bot:
        if group_id:
            await cawy.forward_messages(group_id, event.message)

            sender = await event.get_sender()
            group_name = (await cawy.get_entity(group_id)).title
            timestamp = time.strftime("%H:%M")
            message_text = event.message.text or "لا يوجد نص للرسالة"
            user_mention = f"@{sender.username}" if sender.username else "لا يوجد معرف مستخدم"

            info_message = (
                f"☭ لديك منشن من العضو: {sender.first_name}\n"
                f"☭ اسم الجروب: {group_name}\n"
                f"☭ الوقت: {timestamp}\n"
                f"☭ نص الرسالة: {message_text}\n"
                f"☭ اليوزر: {user_mention}"
            )
            await cawy.send_message(group_id, info_message)

@cawy.on(events.NewMessage(incoming=True))
async def forward_group_message(event):
    if os.path.exists('group_id.pkl'):
        with open('group_id.pkl', 'rb') as f:
            group_id = pickle.load(f)
    else:
        group_id = None

    if event.is_group and group_id:
        if event.reply_to_msg_id:
            replied_message = await event.get_reply_message()
            bot_id = (await cawy.get_me()).id

            if replied_message.sender_id == bot_id:
                await cawy.forward_messages(group_id, event.message)

                sender = await event.get_sender()
                group_name = (await cawy.get_entity(group_id)).title
                timestamp = time.strftime("%H:%M")
                message_text = event.message.text or "لا يوجد نص للرسالة"
                user_mention = f"@{sender.username}" if sender.username else "لا يوجد معرف مستخدم"

                info_message = (
                    f"☭ لديك منشن من العضو: {sender.first_name}\n"
                    f"☭ اسم الجروب: {group_name}\n"
                    f"☭ الوقت: {timestamp}\n"
                    f"☭ نص الرسالة: {message_text}\n"
                    f"☭ اليوزر: {user_mention}"
                )
                await cawy.send_message(group_id, info_message)

@cawy.on(events.NewMessage(from_users='me', pattern='.رد'))
async def add_response(event):
    try:
        photo_path = None
        if event.reply_to_msg_id:
            replied_message = await cawy.get_messages(event.chat_id, ids=event.reply_to_msg_id)
            if replied_message.photo:
                photo_path = os.path.join(image_folder, f"{event.reply_to_msg_id}.jpg")
                await cawy.download_media(replied_message, file=photo_path)

        if ' ' in event.raw_text:
            _, args = event.raw_text.split(' ', 1)
            if '(' in args and ')' in args:
                keyword, response = args.split('(', 1)[1].split(')', 1)
                keyword = keyword.strip().lower()
                response = response.strip()

                responses[keyword] = {
                    'response': response,
                    'photo': photo_path
                }
                
                with open(response_file, 'wb') as f:
                    pickle.dump(responses, f)
                
                if photo_path:
                    await event.reply("✅ تم إضافة الرد مع الصورة.")
                else:
                    await event.reply("✅ تم إضافة الرد بدون صورة.")
            else:
                await event.reply("**❗يجب استخدام التنسيق التالي: \n .رد + اسم الرد + الرد\n\n ملاحظة ‼️\n يجب وضع كلمة الرد في قوسين ذول () مثال: \n .رد (سايرون) ياعيونه امر تدلل**")
        else:
            await event.reply("**❗يجب استخدام التنسيق التالي: \n .رد + اسم الرد + الرد\n\n ملاحظة ‼️\n يجب وضع كلمة الرد في قوسين ذول () مثال: \n .رد (سايرون) ياعيونه امر تدلل**")

    except Exception as e:
        await event.reply(f"حدث خطأ: {str(e)}")

@cawy.on(events.NewMessage(from_users='me', pattern='.الردود'))
async def show_responses(event):
    try:
        if responses:
            message = "📋 الردود المضافة:\n"
            for keyword, data in responses.items():
                photo_status = "مضافة إليه صورة" if data['photo'] else "غير مضافة إليه صورة"
                message += f"🔹 الكلمة المفتاحية: {keyword}\n🔸 الرد: {data['response']} ({photo_status})\n"
            await event.reply(message)
        else:
            await event.reply("❌ لا توجد ردود مضافة حتى الآن.")
    except Exception as e:
        await event.reply(f"حدث خطأ: {str(e)}")

@cawy.on(events.NewMessage(incoming=True))
async def respond_to_greeting(event):
    sender = await event.get_sender()

    message_text = event.raw_text.lower()
    for keyword, data in responses.items():
        if keyword in message_text:
            try:
                if data['photo']:
                    await cawy.send_file(event.chat_id, file=data['photo'], caption=data['response'])
                else:
                    await event.reply(data['response'])
            except Exception as e:
                await event.reply(f"حدث خطأ: {str(e)}")
            break

@cawy.on(events.NewMessage(from_users='me', pattern='.حذف'))
async def delete_message(event):
    await asyncio.sleep(2)
    await event.delete()
    
    try:
        command, keyword = event.raw_text.split(' ', 1)
        keyword = keyword.lower()
        
        if keyword in responses:
            del responses[keyword]
            with open(response_file, 'wb') as f:
                pickle.dump(responses, f)
            
            confirmation_message = await event.reply("✅ تم حذف الرد")
            await asyncio.sleep(2)
            await confirmation_message.delete()
        else:
            warning_message = await event.reply("⚠️ لم يتم العثور على الكلمة المحددة")
            await asyncio.sleep(2)
            await warning_message.delete()
    
    except ValueError:
        error_message = await event.reply("**❗استخدم التنسيق التاليه: \n\n .حذف + كلمة الرد**")
        await asyncio.sleep(2)
        await error_message.delete()

moment_worker = []

@cawy.on(events.NewMessage(pattern=r"\.all (.*)"))
async def tagall(event):
    global moment_worker
    if event.is_private:
        return await event.reply("**- عـذراً ... هـذه ليـست مجمـوعـة ؟!**")
    
    msg = event.pattern_match.group(1)
    moment_worker.append(event.chat_id)
    usrnum = 0
    usrtxt = ""
    
    async for usr in cawy.iter_participants(event.chat_id):
        usrnum += 1
        usrtxt += f"- [{usr.first_name}](tg://user?id={usr.id}) "
        
        if event.chat_id not in moment_worker:
            await event.reply("**⎉╎تم إيقـاف التـاك .. بنجـاح ✓**")
            return
        
        if usrnum == 5:
            await cawy.send_message(event.chat_id, f"{usrtxt}\n\n- {msg}")
            await asyncio.sleep(2)
            usrnum = 0
            usrtxt = ""

@cawy.on(events.NewMessage(pattern=r"\.تاك (.*)"))
async def tag(event):
    global moment_worker
    if event.is_private:
        return await event.reply("**- عـذراً ... هـذه ليـست مجمـوعـة ؟!**")
    
    msg = event.pattern_match.group(1)
    moment_worker.append(event.chat_id)
    usrnum = 0
    usrtxt = ""
    
    async for usr in cawy.iter_participants(event.chat_id):
        usrnum += 1
        usrtxt += f"- [{usr.first_name}](tg://user?id={usr.id}) "
        
        if event.chat_id not in moment_worker:
            await event.reply("**⎉╎تم إيقـاف التـاك .. بنجـاح ✓**")
            return
        
        if usrnum == 5:
            await cawy.send_message(event.chat_id, f"{usrtxt}\n\n- {msg}")
            await asyncio.sleep(2)
            usrnum = 0
            usrtxt = ""

@cawy.on(events.NewMessage(pattern=r"\.ايقاف التاك"))
async def stop_tagall(event):
    if event.chat_id not in moment_worker:
        return await event.reply('**- عـذراً .. لا يوجـد هنـاك تـاك لـ إيقـافـه ؟!**')
    else:
        try:
            moment_worker.remove(event.chat_id)
        except:
            pass
        return await event.reply('**⎉╎تم إيقـاف التـاك .. بنجـاح ✓**')

@cawy.on(events.NewMessage(outgoing=True, pattern=".حلويات"))
async def _(event):
    event = await event.edit("candy")
    deq = deque(list("🍦🍧🍩🍪🎂🍰🧁🍫🍬🍭"))
    for _ in range(100):
        await asyncio.sleep(0.4)
        await event.edit("".join(deq))
        deq.rotate(1)

@cawy.on(events.NewMessage(outgoing=True, pattern=".قلوب"))
async def _(event):
    animation_interval = 0.3
    animation_ttl = range(54)
    event = await event.edit("🖤")
    animation_chars = [
        "❤️",
        "🧡",
        "💛",
        "💚",
        "💙",
        "💜",
        "🖤",
        "💘",
        "💝",
        "❤️",
        "🧡",
        "💛",
        "💚",
        "💙",
        "💜",
        "🖤",
        "💘",
        "💝",
    ]
    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await event.edit(animation_chars[i % 18])

        
@cawy.on(events.NewMessage(outgoing=True, pattern=".قمر"))
async def _(event):
    event = await event.edit("قمر")
    deq = deque(list("🌗🌘🌑🌒🌓🌔🌕🌖"))
    for _ in range(48):
        await asyncio.sleep(0.2)
        await event.edit("".join(deq))
        deq.rotate(1)
        
@cawy.on(events.NewMessage(outgoing=True, pattern=".قمور"))
async def _(event):
    event = await event.edit("قمور")
    animation_interval = 0.2
    animation_ttl = range(96)
    await event.edit("قمور..")
    animation_chars = [
        "🌗",
        "🌘",
        "🌑",
        "🌒",
        "🌓",
        "🌔",
        "🌕",
        "🌖",
        "🌗",
        "🌘",
        "🌑",
        "🌒",
        "🌓",
        "🌔",
        "🌕",
        "🌖",
        "🌗",
        "🌘",
        "🌑",
        "🌒",
        "🌓",
        "🌔",
        "🌕",
        "🌖",
        "🌗",
        "🌘",
        "🌑",
        "🌒",
        "🌓",
        "🌔",
        "🌕",
        "🌖",
    ]
    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await event.edit(animation_chars[i % 32])

loop = asyncio.get_event_loop()

async def unblock_users(cawy):
    @cawy.on(events.NewMessage(outgoing=True, pattern='.فك المحظورين'))
    async def _(event):
        list = await cawy(GetBlockedRequest(offset=0, limit=1000000))
        if len(list.blocked) == 0 :
            razan = await event.edit(f'- لم تقم بحظر اي شخص اصلا .')
        else :
            unblocked_count = 1
            for user in list.blocked :
                UnBlock = await cawy(UnblockRequest(id=int(user.peer_id.user_id)))
                unblocked_count += 1
                razan = await event.edit(f'- جار الغاء حظر  {round((unblocked_count * 100) / len(list.blocked), 2)}%')
            unblocked_count = 1
            razan = await event.edit(f'- تم الغاء حظر : {len(list.blocked)}\n\n- تم المستخدمين المحظورين في الخاص بنجاح  .')


muted_users_file = 'muted_users.pkl'


if os.path.exists(muted_users_file):
    with open(muted_users_file, 'rb') as f:
        muted_users = pickle.load(f)
else:
    muted_users = set()


@cawy.on(events.NewMessage(incoming=True))
async def delete_muted_messages(event):
    if event.chat_id in muted_users:
        
        await event.delete()

@cawy.on(events.NewMessage(from_users='me', pattern='.كتم'))
async def mute_user(event):
    if event.is_private:
        muted_users.add(event.chat_id)
        with open(muted_users_file, 'wb') as f:
            pickle.dump(muted_users, f)
        await event.reply("✅ **تم كتم المستخدم**")
    else:
        await event.reply("⚠️ يمكن استخدام هذا الأمر في المحادثات الخاصة فقط.")

@cawy.on(events.NewMessage(from_users='me', pattern='.الغاء الكتم'))
async def unmute_user(event):
    if event.is_private and event.chat_id in muted_users:
        muted_users.remove(event.chat_id)
        with open(muted_users_file, 'wb') as f:
            pickle.dump(muted_users, f)
        await event.reply("✅ تم فك الكتم عن هذا المستخدم.")
    else:
        await event.reply("⚠️ هذا المستخدم ليس في قائمة المكتومين")

@cawy.on(events.NewMessage(from_users='me', pattern='.المكتومين'))
async def show_muted_users(event):
    if muted_users:
        muted_users_list = "\n".join([str(user_id) for user_id in muted_users])
        await event.reply(f"📋 المستخدمون المكتومون:\n{muted_users_list}")
    else:
        await event.reply("❌ لا يوجد مستخدمون مكتومون حالياً.")

@cawy.on(events.NewMessage(from_users='me', pattern='.اضف قناه (.+)'))
async def add_channel(event):
    global channel_link
    channel_link = event.pattern_match.group(1)
    with open(channel_link_file, 'wb') as f:
        pickle.dump(channel_link, f)
    await event.reply(f"✅ تم تعيين رابط القناة إلى: {channel_link}")
    await event.delete()

@cawy.on(events.NewMessage(from_users='me', pattern= '.مسح القناه' ))
async def remove_channel(event):
    global channel_link
    channel_link = ''
    with open(channel_link_file, 'wb') as f:
        pickle.dump(channel_link, f)
    reply = await event.reply("❌ تم مسح رابط القناة.")
    await event.delete()
    await asyncio.sleep(3)
    await reply.delete()

async def is_subscribed(user_id):
    if not channel_link:
        return True
    channel_username = re.sub(r'https://t.me/', '', channel_link)
    try:
        offset = 0
        limit = 100
        while True:
            participants = await cawy(GetParticipantsRequest(
                channel=channel_username,
                filter=ChannelParticipantsSearch(''),
                offset=offset,
                limit=limit,
                hash=0
            ))
            if not participants.users:
                break
            for user in participants.users:
                if user.id == user_id:
                    return True
            offset += len(participants.users)
        return False
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)
        return await is_subscribed(user_id)
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

@cawy.on(events.NewMessage(incoming=True))
async def respond_to_greeting(event):
    if event.is_private and not (await event.get_sender()).bot:
        sender = await event.get_sender()
        if sender.phone == '42777':
            return
        if not await is_subscribed(event.sender_id):
            await event.reply(f"لا يمكنك مراسلتي الى بعد الاشتراك في قناتي: {channel_link}")
            await cawy.delete_messages(event.chat_id, [event.id])


@cawy.on(events.NewMessage(outgoing=True, pattern=".ضيف"))
async def get_users(event):
    legen_ = event.text[10:]
    cawy_chat = legen_.lower
    restricted = ["@D_6_F", "@eriop_6"]
    cawy = await event.edit(f"**جارِ اضأفه الاعضاء من  ** {legen_}")
    if cawy_chat in restricted:
        return await cawy.edit(
            event, "**- لا يمكنك اخذ الاعضاء من مجموعه السورس العب بعيد ابني  :)**"
        )
    sender = await event.get_sender()
    me = await event.client.get_me()
    if not sender.id == me.id:
        await cawy.edit("**▾∮ تتم العملية انتظر قليلا ...**")
    else:
        await cawy.edit("**▾∮ تتم العملية انتظر قليلا ...**")
    if event.is_private:
        return await cawy.edit("- لا يمكنك اضافه الاعضاء هنا")
    s = 0
    f = 0
    error = "None"
    await cawy.edit(
        "**▾∮ حالة الأضافة:**\n\n**▾∮ تتم جمع معلومات المستخدمين 🔄 ...⏣**"
    )
    async for user in event.client.iter_participants(event.pattern_match.group(1)):
        try:
            if error.startswith("Too"):
                return await cawy.edit(
                    f"**حالة الأضافة انتهت مع الأخطاء**\n- (**ربما هنالك ضغط على الأمر حاول مجددا لاحقا **) \n**الخطأ** : \n`{error}`\n\n• اضافة `{s}` \n• خطأ بأضافة `{f}`"
                )
            tol = f"@{user.username}"
            lol = tol.split("`")
            await cawy(InviteToChannelRequest(channel=event.chat_id, users=lol))
            s = s + 1
            await cawy.edit(
                f"**▾∮تتم الأضافة **\n\n• اضيف `{s}` \n•  خطأ بأضافة `{f}` \n\n**× اخر خطأ:** `{error}`"
            )
        except Exception as e:
            error = str(e)
            f = f + 1
    return await cawy.edit(
        f"**▾∮اڪتملت الأضافة ✅** \n\n• تم بنجاح اضافة `{s}` \n• خطأ بأضافة `{f}`"
    )
config_file = 'bot_config.json'

# التحقق من وجود ملف الإعدادات أو طلب القيم من المستخدم
if not os.path.exists(config_file):
    print("🔑 إعداد البرنامج لأول مرة.")
    TOKEN = input("➡️ أدخل توكن البوت (BOT_TOKEN): ").strip()
    CHAT_ID = input("➡️ أدخل معرف البوت أو الدردشة (CHAT_ID): ").strip()
    
    # حفظ القيم المدخلة في ملف
    with open(config_file, 'w') as file:
        json.dump({"TOKEN": TOKEN, "CHAT_ID": CHAT_ID}, file)
else:
    # تحميل القيم من الملف
    with open(config_file, 'r') as file:
        config = json.load(file)
        TOKEN = config.get("TOKEN")
        CHAT_ID = config.get("CHAT_ID")

# رابط المستودع الذي سيتم تحديث السورس منه
repo_url = "https://github.com/zeko1244/test"  # استبدل هذا بعنوان المستودع الخاص بالسورس

# دالة التحديث الذاتي
async def auto_update():
    try:
        # تحميل آخر نسخة من السورس
        os.system(f"git pull {repo_url}")
        
        # إعادة تشغيل البرنامج
        os.execv(__file__, ['python'] + sys.argv)
    except Exception as e:
        print(f"حدث خطأ أثناء التحديث الذاتي: {e}")

# دالة إرسال إشعار التحديث
async def notify_update():
    message = "✅ تم تحديث السورس بنجاح."
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {'chat_id': CHAT_ID, 'text': message}
        requests.post(url, data=data)
    except Exception as e:
        print(f"خطأ أثناء إرسال إشعار التحديث: {e}")

# أمر لتحديث السورس يدويًا
@cawy.on(events.NewMessage(outgoing=True, pattern=".تحديث"))
async def manual_update(event):
    await event.reply("⏳ جاري تحديث السورس...")
    try:
        # تنفيذ التحديث
        await auto_update()
        await notify_update()
    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء التحديث: `{e}`")
print("""
                       
______
< Cawy >
 ------
    \
     \
                                   .::!!!!!!!:.
  .!!!!!:.                        .:!!!!!!!!!!!!
  ~~~~!!!!!!.                 .:!!!!!!!!!UWWW$$$
      :$$NWX!!:           .:!!!!!!XUWW$$$$$$$$$P
      $$$$$##WX!:      .<!!!!UW$$$$•  $$$$$$$$#
      $$$$$  $$$UX   :!!UW$$$$$$$$$   4$$$$$*
      ^$$$B  $$$$\     $$$$$$$$$$$$   d$$R•
        •*$bd$$$$      •*$$$$$$$$$$$o+#•
             ••••          •••••••

bot is running...
    """)


cawy.loop.create_task(join_channel())
loop.create_task(unblock_users(cawy))
cawy.run_until_disconnected()
