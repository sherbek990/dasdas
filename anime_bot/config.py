# =============================================
#   SOZLAMALAR - Shu yerda o'zgartiring
# =============================================

# Bot tokeni (@BotFather dan oling)
BOT_TOKEN = "8559859729:AAEFxLJvtPF72Chh8_pEHoKPj1XoiF6VOdg"

# Admin Telegram ID lari (bir nechta bo'lishi mumkin)
ADMIN_IDS = [5985915849]  # O'z ID ingizni kiriting

# Majburiy obuna kanallar
# Format: {"channel_id": "@kanal_nomi", "invite_link": "https://t.me/..."}
REQUIRED_CHANNELS = [
    {
        "channel_id": "@AniFirstUZ",
        "invite_link": "https://t.me/AniFirstUZ",
        "name": "Asosiy Kanal"
    },
    # Ko'proq kanal qo'shish uchun shu formatda davom eting
]

# Ma'lumotlar bazasi fayli
DB_PATH = "database/anime_bot.db"

# VIP narxi (so'm)
VIP_PRICE = 20000

# Reklama matni (VIP bo'lmaganlar uchun)
AD_TEXT = """
╔══════════════════════╗
║  📢 E'lon / Reklama  ║
╚══════════════════════╝

🎯 Bu yerga o'z reklamangizni joylang!
📩 Admin: @Ortikovv_Sh

━━━━━━━━━━━━━━━━━━━━━━
"""

# To'lov rekvizitlari
PAYMENT_CARD = "8600 0000 0000 0000"  # Karta raqami
PAYMENT_NAME = "Ortiqov Sherbek"         # Karta egasi
PAYMENT_ADMIN = "@Ortikovv_Sh"     # To'lovni tasdiqlash uchun admin

# Har sahifada nechta epizod ko'rsatilsin
EPISODES_PER_PAGE = 25
