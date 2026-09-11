import asyncio
import random
from datetime import date

from pyromod import listen
from pyrogram import Client, filters, idle
from pyrogram import __version__ as v
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from telethon import TelegramClient
from telethon import __version__ as v2
from telethon.sessions import StringSession

from kvsqlite.sync import Client as DB
from pyrogram.errors import (
    FloodWait, SessionPasswordNeeded, PhoneCodeExpired,
    PasswordHashInvalid, PhoneNumberInvalid, PhoneCodeInvalid
)
from telethon.errors import (
    PhoneNumberInvalidError, PhoneCodeInvalidError,
    PhoneCodeExpiredError, SessionPasswordNeededError,
    PasswordHashInvalidError
)

# ==================== الإعدادات الأساسية ====================
ownerID = 5830007992 # ايدي الادمن (علي)
api_hash = "1c3e709f42b19ff09a23e244df5c7379" # ايبي هاش 
api_id = 31634346 # ايبي ايدي
token = "7452969875:AAGEr_-b0NHJH1Xb7ufJLP7CfBghz0FzU_o" # توكن البوت

BOT_ID = token.split(":")[0]
DB_KEY = "db" + BOT_ID
botdb = DB('botdb.sqlite')

# دمج العملاء في عميل واحد لضمان دقة العمل وعدم ضياع التحديثات
app = Client(
    name="session_bot",
    api_id=api_id, 
    api_hash=api_hash,
    bot_token=token, 
    in_memory=True
)

# ==================== قوائم الأزرار ====================
STARTKEY = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("≈ إذاعة للمستخدمين ≈", callback_data="broadcast")],
        [
            InlineKeyboardButton("≈ الاحصائيات ≈", callback_data="stats"),
            InlineKeyboardButton("≈ الأدمنية ≈", callback_data="adminstats"),
            InlineKeyboardButton("≈ المحظورين ≈", callback_data="bannedstats"),
        ],
        [
            InlineKeyboardButton("≈ كشف مستخدم ≈", callback_data="whois"),
            InlineKeyboardButton("≈ حظر مستخدم ≈", callback_data="ban"),
        ],
        [InlineKeyboardButton("≈ الغاء حظر مستخدم ≈", callback_data="unban")],
        [
            InlineKeyboardButton("≈ رفع ادمن ≈", callback_data="addadmin"),
            InlineKeyboardButton("≈ تنزيل ادمن ≈", callback_data="remadmin"),
        ]
    ]
)

USER_MENU = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("بـايـروجـرام", callback_data="pyro"), 
            InlineKeyboardButton("تـيـلـيـثـون", callback_data="tele")
        ],
        [InlineKeyboardButton("مـعـلـومـات عـن الـبـوت", callback_data="about")]
    ]
)

# ==================== تهيئة قاعدة البيانات ====================
if not botdb.get(DB_KEY):
    data = {"users": [], "admins": [], "banned": []}
    botdb.set(DB_KEY, data)

if ownerID not in botdb.get(DB_KEY)["admins"]:
    data = botdb.get(DB_KEY)
    data["admins"].append(ownerID)
    botdb.set(DB_KEY, data)

# قائمة الهواتف العشوائية للجلسات (قديمة وجديدة)
PHONE_MODELS = [
    # iPhone
    "iPhone 6", "iPhone 7 Plus", "iPhone 8", "iPhone X", "iPhone 11 Pro",
    "iPhone 12 mini", "iPhone 13 Pro", "iPhone 14 Plus", "iPhone 15 Pro Max",
    # Samsung
    "Samsung Galaxy S7", "Samsung Galaxy S9", "Samsung Galaxy S10+", "Samsung Galaxy S20 Ultra",
    "Samsung Galaxy S22", "Samsung Galaxy S23 Ultra", "Samsung Galaxy S24 Ultra",
    "Samsung Galaxy Note 10", "Samsung Galaxy Note 20 Ultra", "Samsung Galaxy A54",
    # Infinix
    "Infinix Hot 10", "Infinix Hot 30", "Infinix Note 11", "Infinix Note 30 Pro",
    "Infinix Zero 8", "Infinix Zero Ultra", "Infinix Smart 7",
    # Xiaomi
    "Xiaomi Mi 9", "Xiaomi Mi 10T", "Xiaomi 12 Pro", "Xiaomi 13 Ultra", "Xiaomi 14 Pro",
    # Redmi
    "Redmi Note 7", "Redmi Note 8 Pro", "Redmi Note 10", "Redmi Note 12 Pro+", "Redmi Note 13 Pro",
    # OnePlus
    "OnePlus 6", "OnePlus 7T Pro", "OnePlus 8T", "OnePlus 9 Pro", "OnePlus 11",
    "OnePlus 12", "OnePlus Nord CE 3",
    # iQOO
    "iQOO 7", "iQOO 9 Pro", "iQOO 11", "iQOO 12 Pro", "iQOO Neo 7",
    # Vivo
    "Vivo V15", "Vivo V21", "Vivo V29", "Vivo X70 Pro", "Vivo X90 Pro+", "Vivo X100 Pro"
]

# دالة العد التنازلي
async def countdown(message, text):
    msg = await message.reply(f"**{text}**\n\n⏳ 5", quote=True)
    for i in range(4, 0, -1):
        await asyncio.sleep(1)
        try:
            await msg.edit(f"**{text}**\n\n⏳ {i}")
        except:
            pass
    await msg.delete()

# ==================== أوامر البداية والإدارة ====================

@app.on_message(filters.command("admin") & filters.private)
async def on_admin(c, m):
    getDB = botdb.get(DB_KEY)
    if m.from_user.id in getDB["banned"]:
        return await m.reply("🚫 تم حظرك من استخدام البوت", quote=True)
        
    if m.from_user.id == ownerID or m.from_user.id in getDB["admins"]:
        await m.reply(f"**• أهلاً بك ⌯ {m.from_user.mention}\n• إليك لوحة تحكم الادمن**", reply_markup=STARTKEY, quote=True)
    else:
        await m.reply("⚠️ هذا الأمر مخصص للإدارة فقط.", quote=True)

@app.on_message(filters.command("start") & filters.private)
async def on_start(c, m):
    getDB = botdb.get(DB_KEY)
    if m.from_user.id in getDB["banned"]:
        return await m.reply("🚫 تم حظرك من استخدام البوت", quote=True)
        
    # تسجيل المستخدم إذا كان جديداً
    if m.from_user.id not in getDB["users"]:
        data = getDB
        data["users"].append(m.from_user.id)
        botdb.set(DB_KEY, data)
        for admin in data["admins"]:
            text = f"– New user started the bot :\n\n"
            username = "@" + m.from_user.username if m.from_user.username else "None"
            text += f"𖡋 𝐔𝐒𝐄 ⌯  {username}\n"
            text += f"𖡋 𝐍𝐀𝐌𝐄 ⌯  {m.from_user.mention}\n"
            text += f"𖡋 𝐈𝐃 ⌯  `{m.from_user.id}`\n"
            text += f"𖡋 𝐃𝐀𝐓𝐄 ⌯  **{date.today()}**"
            try: 
                await c.send_message(admin, text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(m.from_user.first_name, user_id=m.from_user.id)]]))
            except: 
                pass
                
    user_data = {
        "name": m.from_user.first_name[:25], 
        "username": m.from_user.username, 
        "mention": m.from_user.mention(m.from_user.first_name[:25]),
        "id": m.from_user.id
    }
    botdb.set(f"USER:{m.from_user.id}", user_data)
    
    await m.reply(
        f"- مرحـبـًا عـزيـزي 🙋 {m.from_user.mention}،\nفي بوت استخـراج جلسات.\n- لبـدء استخـراج الجلسة اختـر الجلسـة بالاسفل.\n- إذا كنـت تريـد أن يكون حسـابك في أمـان تام فاختر بايروجـرام أمـا إذا كـان رقمك حقيقـي فاختر تيليثون .\n\n- ملاحظـة :\n- احـذر مشاركـة الكود لأحـد لأنه يستطيـع اختراق حسـابك ⚠️ .",
        reply_markup=USER_MENU, 
        quote=True
    )

# ==================== معالجة الاستجابات (Callbacks) ====================

@app.on_callback_query()
async def on_Callback(c, m):
    # مسح الحالات للإدارة
    def clear_admin_states(user_id):
        keys = ["broad", "whois", "ban", "add", "rem", "unban"]
        for key in keys:
            botdb.delete(f"{key}:{user_id}")
            
    is_admin = m.from_user.id == ownerID or m.from_user.id in botdb.get(DB_KEY)["admins"]

    # ----------------- قسم الإدارة -----------------
    if m.data == "broadcast" and is_admin:
        clear_admin_states(m.from_user.id)
        botdb.set(f"broad:{m.from_user.id}", True)
        await m.edit_message_text("• أرسل الإذاعة الآن ( صورة ، نص ، ملصق ، ملف ، صوت )\n• للإلغاء ارسل الغاء ", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="back")]]))
        
    elif m.data == "whois" and is_admin:
        clear_admin_states(m.from_user.id)
        botdb.set(f"whois:{m.from_user.id}", True)
        await m.edit_message_text("• ارسل الآن ايدي المستخدم للكشف عنه\n• للإلغاء ارسل الغاء ", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="back")]]))
        
    elif m.data == "ban" and is_admin:
        clear_admin_states(m.from_user.id)
        botdb.set(f"ban:{m.from_user.id}", True)
        await m.edit_message_text("• ارسل الآن ايدي المستخدم لحظره\n• للإلغاء ارسل الغاء ", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="back")]]))
   
    elif m.data == "unban" and is_admin:
        clear_admin_states(m.from_user.id)
        botdb.set(f"unban:{m.from_user.id}", True)
        await m.edit_message_text("• ارسل الآن ايدي المستخدم لرفع حظره\n• للإلغاء ارسل الغاء ", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="back")]]))
   
    elif m.data == "addadmin" and m.from_user.id == ownerID:
        clear_admin_states(m.from_user.id)
        botdb.set(f"add:{m.from_user.id}", True)
        await m.edit_message_text("• ارسل الآن ايدي المستخدم لرفعه ادمن\n• للإلغاء ارسل الغاء ", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="back")]]))
   
    elif m.data == "remadmin" and m.from_user.id == ownerID:
        clear_admin_states(m.from_user.id)
        botdb.set(f"rem:{m.from_user.id}", True)
        await m.edit_message_text("• ارسل الآن ايدي المستخدم لتنزيله من الادمنية\n• للإلغاء ارسل الغاء ", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="back")]]))

    elif m.data == "back" and is_admin:
        clear_admin_states(m.from_user.id)
        await m.edit_message_text(f"**• أهلاً بك ⌯ {m.from_user.mention}\n• إليك لوحة تحكم الادمن**", reply_markup=STARTKEY)
      
    elif m.data == "stats" and is_admin:
        users = len(botdb.get(DB_KEY)["users"])
        await m.answer(f"• احصائيات البوت ⌯ {users}", show_alert=True, cache_time=10)
      
    elif m.data == "adminstats" and is_admin:
        admins = len(botdb.get(DB_KEY)["admins"])
        await m.answer(f"• احصائيات الادمنية ⌯ {admins}\n• سيتم ارسال بيانات كل آدمن", show_alert=True, cache_time=60)
        text = "- الادمنية:\n\n"
        count = 1
        for admin in botdb.get(DB_KEY)["admins"]:
            if count == 101: break
            getUser = botdb.get(f"USER:{admin}")
            if getUser:
                text += f"{count}) {getUser['mention']} ~ (`{getUser['id']}`)\n"
                count += 1
        text += "\n\n—"
        await m.message.reply(text, quote=True)
   
    elif m.data == "bannedstats" and is_admin:
        bans = botdb.get(DB_KEY)["banned"]
        if not bans: 
            return await m.answer("• لا يوجد محظورين", show_alert=True, cache_time=60)
        await m.answer(f"• احصائيات المحظورين ⌯ {len(bans)}\n• سيتم ارسال بيانات كل المحظورين", show_alert=True, cache_time=60)
        text = "- المحظورين:\n\n"
        count = 1
        for banned in bans:
            if count == 101: break
            getUser = botdb.get(f"USER:{banned}")
            if getUser:
                text += f"{count}) {getUser['mention']} ~ (`{getUser['id']}`)\n"
                count += 1
        text += "\n\n—"
        await m.message.reply(text, quote=True)

    # ----------------- قسم الجلسات للمستخدمين -----------------
    elif m.data == "about":
        text = f"🐍 اللـغـة الـبـرمـجـيـة - بـايـثـون\n🔥 اصـدار بايروجرام {v}\n🌱 اصـدار تـيـلـيـثـون {v2}\n\n👤 مـطـور الـبـوت: @WWSVA"
        await m.message.reply(text, quote=True)
        await m.answer()

    elif m.data == "pyro":
        await m.answer()
        rep = await m.message.reply("**⏳ يـعالـج..**", quote=True)
        device = random.choice(PHONE_MODELS)
        client_pyro = Client(f"pyro{m.from_user.id}", api_id, api_hash, device_model=device, in_memory=True)
        await client_pyro.connect()
        await rep.delete()
        
        phone_ask = await m.message.chat.ask("⎆ يـرجـى إرسـال رقـم هاتفـك مـع رمـز الدولة مثــال 📱: \n+963995×××××", reply_to_message_id=m.message.id, filters=filters.text)
        if phone_ask.text == "/start": return
        phone = phone_ask.text
        
        await countdown(phone_ask, "جاري معالجة رقم الهاتف...")
        try:
            send_code = await client_pyro.send_code(phone)
        except PhoneNumberInvalid:
            return await phone_ask.reply("⎆ رقـم الهـاتف الذي أرسلـته غير صالح أعـد استخـراج الجلسـة مـرة أخـرى .\n/start", quote=True)
        except Exception as e:
            return await phone_ask.reply(f"خطأ! ، يرجى المحاولة مرة أخرى لاحقًا 🤠\n/start", quote=True)
            
        hash_code = send_code.phone_code_hash
        code_ask = await m.message.chat.ask("⎆ أرسـل الكـود\n إذا جاءك في هـذه الطريقـة '12345' أرسـل بين كـل رقـم فـراغ\nمثـال : ' 1 2 3 4 5' .", filters=filters.text)
        if code_ask.text == "/start": return
        code = code_ask.text
        
        await countdown(code_ask, "جاري التحقق من الكود...")
        try:
            await client_pyro.sign_in(phone, hash_code, code)
        except SessionPasswordNeeded:
            password_ask = await m.message.chat.ask("⎆ يـرجـى إرسـال التحقق الخـاص بحسـابك ..", filters=filters.text)
            if password_ask.text == "/start": return
            password = password_ask.text
            
            await countdown(password_ask, "جاري فك التحقق بخطوتين...")
            try:
                await client_pyro.check_password(password)
            except PasswordHashInvalid:
                return await password_ask.reply("» التحقـق بخطوتيـن الخـاص بـك غيـر صـالح.\nيرجـى إعـادة استخـراج الجلسـة مـرة أخـرى.\n/start", quote=True)
        except (PhoneCodeInvalid, PhoneCodeExpired):
            return await code_ask.reply("رمز الهاتف غير صالح أو منتهي!", quote=True)
        except Exception:
            pass

        rep = await m.message.reply("**⏳ يتم توليد الجلسة ..**", quote=True)
        get = await client_pyro.get_me()
        text = f'**✅ تم تسجيل الدخول بنجاح\n👤 الاسم الأول : {get.first_name}\n🆔 بطاقة تعريف : {get.id}\n📞 رقم الهاتف : {phone}\n📱 الجهاز : {device}\n🔒 تم حفظ الجلسة في الرسائل المحفوظة**'
        string_session = await client_pyro.export_session_string()
        await rep.delete()
        await client_pyro.send_message('me', f'تم استخراج جلسة بايروجرام {v} \nالجهاز: {device}\n\n`{string_session}`')
        await client_pyro.disconnect()
        await app.send_message(m.message.chat.id, text)

    elif m.data == "tele":
        await m.answer()
        rep = await m.message.reply("**⏳ يـعـالـج..**", quote=True)
        device = random.choice(PHONE_MODELS)
        client_tele = TelegramClient(StringSession(), api_id, api_hash, device_model=device, system_version="Mobile", app_version="1.44.0")
        await client_tele.connect()
        await rep.delete()
        
        phone_ask = await m.message.chat.ask("⎆ يـرجـى إرسـال رقـم هاتفـك مـع رمـز الدولة مثــال 📱: \n+963995××××× ", reply_to_message_id=m.message.id, filters=filters.text)
        if phone_ask.text == "/start": return
        phone = phone_ask.text
        
        await countdown(phone_ask, "جاري معالجة رقم الهاتف...")
        try:
            send_code = await client_tele.send_code_request(phone)
        except PhoneNumberInvalidError:
            return await phone_ask.reply("⎆ رقـم الهـاتف الذي أرسلـته غير صالح أعـد استخـراج الجلسـة مـرة أخـرى .\n/start", quote=True)
        except Exception as e:
            return await phone_ask.reply(f"خطأ! ، يرجى المحاولة مرة أخرى لاحقًا 🤠\n/start", quote=True)
            
        code_ask = await m.message.chat.ask("⎆ أرسـل الكـود\n إذا جاءك في هـذه الطريقـة '12345' أرسـل بين كـل رقـم فـراغ\nمثـال : ' 1 2 3 4 5' .", filters=filters.text)
        if code_ask.text == "/start": return
        code = code_ask.text.replace(" ", "")
        
        await countdown(code_ask, "جاري التحقق من الكود...")
        try:
            await client_tele.sign_in(phone, code, password=None)
        except SessionPasswordNeededError:
            password_ask = await m.message.chat.ask("⎆ يـرجـى إرسـال التحقق الخـاص بحسـابك ..", filters=filters.text)
            if password_ask.text == "/start": return
            password = password_ask.text
            
            await countdown(password_ask, "جاري فك التحقق بخطوتين...")
            try:
                await client_tele.sign_in(password=password)
            except PasswordHashInvalidError:
                return await password_ask.reply("» التحقـق بخطوتيـن الخـاص بـك غيـر صـالح.\nيرجـى إعـادة استخـراج الجلسـة مـرة أخـرى.\n/start", quote=True)
        except (PhoneCodeExpiredError, PhoneCodeInvalidError):
            return await code_ask.reply("رمز الهاتف غير صالح أو منتهي!", quote=True)

        rep = await m.message.reply("**⏳ يتم توليد الجلسة ..**", quote=True)
        get = await client_tele.get_me()
        text = f'**✅ تم تسجيل الدخول بنجاح \n👤 الاسم الأول : {get.first_name}\n🆔 بطاقة تعريف : {get.id}\n📞 رقم الهاتف : {phone}\n📱 الجهاز : {device}\n🔒 تم حفظ الجلسة في الرسائل المحفوظة**'
        string_session = client_tele.session.save()
        await rep.delete()
        await client_tele.send_message('me', f'تم استخراج جلسة تيليثون {v2}\nالجهاز: {device}\n\n`{string_session}`')
        await client_tele.disconnect()
        await app.send_message(m.message.chat.id, text)

# ==================== معالجة ردود الإدارة (إلغاء، إذاعة، حظر...) ====================

@app.on_message(filters.private & ~filters.service)
async def on_messages(c, m):       
    if m.text == "الغاء":
        keys = ["broad", "whois", "ban", "add", "rem", "unban"]
        for key in keys:
            botdb.delete(f"{key}:{m.from_user.id}")
        return await m.reply("• تم إلغاء العملية بنجاح.", quote=True)

    is_admin = m.from_user.id == ownerID or m.from_user.id in botdb.get(DB_KEY)["admins"]
    
    if botdb.get(f"broad:{m.from_user.id}") and is_admin:
        botdb.delete(f"broad:{m.from_user.id}")
        text = "**— جاري إرسال الإذاعة إلى المستخدمين**\n"
        reply = await m.reply(text, quote=True)
        count = 0
        users = botdb.get(DB_KEY)["users"]
        for user in users:
            try:
                await m.copy(user)
                count += 1
                await reply.edit(text + f"**— تم ارسال الإذاعة الى [ {count}/{len(users)} ] مستخدم**")
            except FloodWait as x:
                await asyncio.sleep(x.value)
            except Exception:
                pass
        return True
   
    if m.text and botdb.get(f"whois:{m.from_user.id}") and is_admin:
        botdb.delete(f"whois:{m.from_user.id}")
        getUser = botdb.get(f"USER:{m.text[:15]}")
        if not getUser:
            return await m.reply("– لا يوجد مستخدم بهذا الآيدي", quote=True)
        else:
            name = getUser["name"]
            id = getUser["id"]
            mention = getUser["mention"]
            username = "@" + getUser["username"] if getUser["username"] else "None"
            language = botdb.get(f"LANG:{id}")
            text = f"𖡋 𝐔𝐒𝐄 ⌯  {username}\n𖡋 𝐍𝐀𝐌𝐄 ⌯  {name}\n𖡋 𝐈𝐃 ⌯  `{id}`\n𖡋 𝑳𝐀𝐍𝐆 ⌯  {language}\n𖡋 𝐀𝐂𝐂 𝑳𝐈𝐍𝐊 ⌯  **{mention}**"
            return await m.reply(text, quote=True)
   
    if m.text and botdb.get(f"ban:{m.from_user.id}") and is_admin:
        botdb.delete(f"ban:{m.from_user.id}")
        getUser = botdb.get(f"USER:{m.text[:15]}")
        if not getUser:
            return await m.reply("– لا يوجد مستخدم بهذا الآيدي", quote=True)
        else:
            if getUser["id"] in botdb.get(DB_KEY)["admins"]:
                return await m.reply(f"– لا يمكنك حظر ⌯ {getUser['mention']} ⌯ لأنه ادمن", quote=True)
            if getUser["id"] in botdb.get(DB_KEY)["banned"]:
                return await m.reply(f"– لا يمكنك حظر ⌯ {getUser['mention']} ⌯ لأنه محظور مسبقاً", quote=True)
            data = botdb.get(DB_KEY)
            data["banned"].append(getUser["id"])
            botdb.set(DB_KEY, data)
            text = f"- This user added to blacklist:\n\n𖡋 𝐍𝐀𝐌𝐄 ⌯  {getUser['mention']}\n𖡋 𝐈𝐃 ⌯  `{getUser['id']}`"
            return await m.reply(text, quote=True)
   
    if m.text and botdb.get(f"unban:{m.from_user.id}") and is_admin:
        botdb.delete(f"unban:{m.from_user.id}")
        getUser = botdb.get(f"USER:{m.text[:15]}")
        if not getUser:
            return await m.reply("– لا يوجد مستخدم بهذا الآيدي", quote=True)
        else:
            if not getUser["id"] in botdb.get(DB_KEY)["banned"]:
                return await m.reply(f"– لا يمكنك الغاء حظر ⌯ {getUser['mention']} ⌯ لأنه غير محظور مسبقاً", quote=True)
            data = botdb.get(DB_KEY)
            data["banned"].remove(getUser["id"])
            botdb.set(DB_KEY, data)
            text = f"- This user deleted from blacklist:\n\n𖡋 𝐍𝐀𝐌𝐄 ⌯  {getUser['mention']}\n𖡋 𝐈𝐃 ⌯  `{getUser['id']}`"
            return await m.reply(text, quote=True)
   
    if m.text and botdb.get(f"add:{m.from_user.id}") and m.from_user.id == ownerID:
        botdb.delete(f"add:{m.from_user.id}")
        getUser = botdb.get(f"USER:{m.text[:15]}")
        if not getUser:
            return await m.reply("– لا يوجد مستخدم بهذا الآيدي", quote=True)
        else:
            if getUser["id"] in botdb.get(DB_KEY)["admins"]:
                return await m.reply(f"– لا يمكنك رفع ⌯ {getUser['mention']} ⌯ لأنه ادمن مسبقاً", quote=True)
            data = botdb.get(DB_KEY)
            data["admins"].append(getUser["id"])
            botdb.set(DB_KEY, data)
            text = f"- This user added to admins list:\n\n𖡋 𝐍𝐀𝐌𝐄 ⌯  {getUser['mention']}\n𖡋 𝐈𝐃 ⌯  `{getUser['id']}`"
            return await m.reply(text, quote=True)
   
    if m.text and botdb.get(f"rem:{m.from_user.id}") and m.from_user.id == ownerID:
        botdb.delete(f"rem:{m.from_user.id}")
        getUser = botdb.get(f"USER:{m.text[:15]}")
        if not getUser:
            return await m.reply("– لا يوجد مستخدم بهذا الآيدي", quote=True)
        else:
            if getUser["id"] not in botdb.get(DB_KEY)["admins"]:
                return await m.reply(f"– لا يمكنك تنزيل ⌯ {getUser['mention']} ⌯ لأنه ليس ادمن", quote=True)
            if getUser["id"] == ownerID:
                return await m.reply(f"– لا يمكنك تنزيل ⌯ {getUser['mention']} ⌯ لأنه مالك البوت", quote=True)
            data = botdb.get(DB_KEY)
            data["admins"].remove(getUser["id"])
            botdb.set(DB_KEY, data)
            text = f"- This user deleted from admins list:\n\n𖡋 𝐍𝐀𝐌𝐄 ⌯  {getUser['mention']}\n𖡋 𝐈𝐃 ⌯  `{getUser['id']}`"
            return await m.reply(text, quote=True)

# ==================== تشغيل البوت ====================
app.start()
print("تم تشغيل البوت بنجاح - تمت برمجة التحديثات @WWSVA")
idle()

