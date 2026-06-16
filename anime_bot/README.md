# 🎬 Anime Telegram Bot

Anime kontentini boshqarish va yetkazib berish uchun to'liq Telegram bot.

---

## 📦 O'rnatish

### 1. Python o'rnatish
Python 3.10 yoki yangroq kerak: https://python.org

### 2. Fayllarni yuklab olish va papkaga kirish
```bash
cd anime_bot
```

### 3. Kerakli kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Sozlamalarni kiritish — `config.py` faylini oching:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"   # @BotFather dan oling
ADMIN_IDS = [123456789]             # O'z Telegram ID ingiz
PAYMENT_CARD = "8600 0000 0000 0000"
PAYMENT_NAME = "Ism Familiya"
PAYMENT_ADMIN = "@sizning_username"
```

**Telegram ID ni qanday bilish?** — @userinfobot ga /start yuboring.

**Bot token qanday olish?**
1. Telegramda @BotFather ga /start yuboring
2. /newbot buyrug'ini yuboring
3. Bot nomini va username kiriting
4. Token beriladi — uni config.py ga joylashtiring

### 5. Botni ishga tushirish
```bash
python bot.py
```

---

## ⚙️ Admin buyruqlari

| Buyruq | Tavsif |
|--------|--------|
| `/admin` | Admin panel va statistika |
| `/addanime` | Yangi anime qo'shish |
| `/addep` | Epizod qo'shish |
| `/delanime KOD` | Anime o'chirish (masalan: `/delanime NRTO`) |
| `/delep KOD RAQAM` | Epizod o'chirish (masalan: `/delep NRTO 5`) |
| `/setvip ID [kunlar]` | VIP berish (masalan: `/setvip 123456 30`) |
| `/payments` | Kutayotgan to'lovlar |
| `/broadcast` | Hammaga xabar yuborish |
| `/stats` | Bot statistikasi |

---

## 🎬 Anime qo'shish

`/addanime` buyrug'ini bosib quyidagi formatda yuboring:

```
Kod: NRTO
Nomi (UZ): Naruto
Nomi (EN): Naruto
Nomi (RU): Наруто
Janr: Aksyon, Fantastika
Yil: 2002
Mamlakat: Yaponiya
Til: O'zbekcha
Tavsif: Yosh ninja Naruto Uzumaki kuchli bo'lish va hokimlik qo'lga kiritish uchun kurashadi.
```

Keyin `/addep` buyrug'i orqali videolarni qo'shing.

---

## 💎 VIP imkoniyatlari

| Xususiyat | Oddiy | VIP |
|-----------|-------|-----|
| Nom bo'yicha qidirish | ✅ | ✅ |
| Kod bo'yicha qidirish | ✅ | ✅ |
| Janr bo'yicha qidirish | ❌ | ✅ |
| Yangi animalar | ❌ | ✅ |
| Top animalar | ❌ | ✅ |
| Reklamasiz tomosha | ❌ | ✅ |
| Majburiy obunasiz | ❌ | ✅ |

---

## 📂 Loyiha tuzilmasi

```
anime_bot/
├── bot.py              # Asosiy fayl
├── config.py           # Sozlamalar
├── requirements.txt    # Kutubxonalar
├── database/
│   ├── db.py          # Barcha DB amallar
│   └── anime_bot.db   # Ma'lumotlar bazasi (avtomatik yaratiladi)
├── handlers/
│   ├── start.py       # /start va obuna tekshirish
│   ├── search.py      # Barcha qidiruv usullari
│   ├── episodes.py    # Epizod ko'rish
│   ├── vip.py         # VIP sotib olish
│   ├── account.py     # Hisob va pul kiritish
│   └── admin.py       # Admin panel
└── utils/
    ├── keyboards.py   # Barcha tugmalar
    └── subscription.py # Obuna tekshirish
```

---

## 🔧 Hosting (Server)

Botni doimo ishlashi uchun server kerak:
- **VPS** — Faqatcloud, Timeweb, Hostinger VPS (arzon)
- **Railway.app** — Bepul boshlash mumkin
- **PythonAnywhere** — Bepul plan bor

### VPS da ishga tushirish (Linux):
```bash
# Screen yoki tmux bilan fon rejimida ishlatish
screen -S animebot
python bot.py
# Ctrl+A, D — fon rejimga o'tish
```

---

## ❓ Yordam

Muammo bo'lsa — `config.py` dagi `PAYMENT_ADMIN` ga murojaat qiling.
