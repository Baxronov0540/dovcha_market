# Dovcha Market 🛒

Dovcha Market — **FastAPI** asosida qurilgan onlayn savdo platformasi (e-commerce REST API). Foydalanuvchilar mahsulotlarni ko'rishi, savatga qo'shishi, buyurtma berishi va do'kon ochishi mumkin.

---

## 🛠 Texnologiyalar

| Texnologiya | Maqsad |
|---|---|
| **FastAPI** | API framework |
| **SQLAlchemy** | ORM |
| **Alembic** | Migration |
| **PostgreSQL** | Ma'lumotlar bazasi |
| **Redis** | Email tasdiqlash kodi saqlash |
| **Celery** | Asinxron email yuborish |
| **Passlib (argon2)** | Parol hashlash |
| **python-jose** | JWT token |

---

## 📋 Texnik Topshiriq (TZ)

### Foydalanuvchi rollari

| Rol | Ruxsatlar |
|---|---|
| **Anonim** | Mahsulotlarni ko'rish, qidirish, kategoriya bo'yicha filtrlash |
| **Oddiy user** | Savatga qo'shish, buyurtma berish, izoh yozish, like bosish |
| **Verified user** | Do'kon ochish (admin tasdiqlaydi) |
| **Staff** | Mahsulot qo'shish, do'kon qo'shish, chegirma qo'shish |
| **Admin** | Barcha huquq + promokod qo'shish |

### Asosiy modullar

#### 1. Auth
- `POST /auth/register` — Ro'yxatdan o'tish (email tasdiqlash bilan)
- `POST /auth/verify/{code}` — Email tasdiqlash
- `POST /auth/login` — Tizimga kirish (JWT token)
- `POST /auth/logout` — Chiqish (token blacklist)
- `POST /auth/refresh` — Access token yangilash
- `POST /auth/change/password` — Parol o'zgartirish

#### 2. Users
- `GET /users/me` — Profil ko'rish
- `PATCH /users/me/update` — Profilni tahrirlash
- `POST /users/avatar/upload` — Avatar yuklash
- `DELETE /users/avatar/delete` — Avatarni o'chirish
- `POST /users/me/deactivate` — Akkauntni o'chirish

#### 3. Shop (Do'kon)
- Faqat `is_verified=True` foydalanuvchilar do'kon ochishi mumkin
- `POST /shop/create` — Do'kon yaratish (email orqali tasdiqlash)
- `POST /shop/verify/{code}` — Do'konni faollashtirish
- `PATCH /shop/{id}` — Do'kon ma'lumotlarini yangilash
- `PATCH /shop/image/{id}` — Do'kon rasmi yuklash
- `GET /shop/list` — Do'konlar ro'yxati (filter: name, rating)

#### 4. Items (Mahsulotlar)
- Chegirma tizimi: `ItemDiscount` + `Discount` orqali guruhli aksiyalar
- Response'da `price` (asl narx) va `discounted_price` (chegirmali narx) birga qaytadi
- `POST /product/create` — Mahsulot qo'shish (do'kon egasi)
- `GET /product/list` — Ro'yxat (filter: category, sort: price/rating/name)
- `GET /product/one/{id}` — Bitta mahsulot
- `PUT /product/update/{id}` — Tahrirlash

#### 5. Cart (Savat)
- `POST /users/cart/items` — Savatga qo'shish
- `GET /users/cart/list` — Savat tarkibi
- `PATCH /users/cart/clear` — Savatni tozalash

#### 6. Orders (Buyurtmalar)
- `POST /order/create` — Buyurtma berish (savat → order, narx snapshot saqlanadi)
- `GET /order/list` — Mening buyurtmalarim
- `GET /order/{id}` — Buyurtma tafsilotlari
- `PATCH /order/{id}/cancel` — Bekor qilish (mahsulot miqdori qaytariladi)

#### 7. Payments (To'lovlar)
- `POST /payments/create` — To'lov yaratish
- `GET /payments/list` — To'lovlar tarixi
- `PATCH /payments/{id}/pay` — To'lovni tasdiqlash (order → `processing`)

#### 8. Discounts (Chegirmalar)
- `Discount` — guruhli chegirma kampaniyalari (foizda)
- `ItemDiscount` — mahsulotga chegirma bog'lash (muddati bilan)
- `Promokod` — buyurtmaga chegirma kodi (`usage_limit` bilan)

#### 9. Comments & Ratings
**Mahsulot izohlari:**
- `POST /comment/{item_id}` — Izoh + reyting qo'shish
- `GET /comment/list/{item_id}` — Ro'yxat

**Do'kon izohlari:**
- `POST /shop-comments/create/{shop_id}` — Izoh + reyting (faqat xarid qilgan userlar)
- `GET /shop-comments/list/{shop_id}` — Ro'yxat
- Do'kon o'rtacha reytingi avtomatik hisoblanadi

#### 10. Location & Delivery
- `DeliveryPoint` — yetkazib berish punktlari (koordinata, ish vaqti)
- `Region` — viloyatlar

---

## 🚀 Loyihani ishga tushirish

```bash
# 1. Virtual muhit va kutubxonalar
uv sync

# 2. .env faylini sozlash
cp .env.example .env  # o'zingizning ma'lumotlaringizni kiriting

# 3. Migration
uv run alembic upgrade head

# 4. Serverni ishga tushirish
uv run uvicorn app.main:app --reload
```

**Swagger UI:** http://localhost:8000/docs

---

## 📁 Loyiha tuzilishi

```
app/
├── models.py         # Barcha SQLAlchemy modellari
├── schemas/          # Pydantic request/response schemalari
├── routers/          # API endpointlar
├── dependencies.py   # JWT va auth dependency-lar
├── database.py       # DB session
├── config.py         # Environment o'zgaruvchilar
├── utils.py          # JWT, password, redis yordamchilar
└── celery.py         # Celery task-lar
alembic/              # Migration fayllari
```

---

## 🔐 Autentifikatsiya

JWT Bearer token ishlatiladi. Token olish:
1. `POST /auth/register` → email confirmation
2. `POST /auth/verify/{code}` → aktiv bo'ladi
3. `POST /auth/login` → `access_token` + `refresh_token`
4. So'rovlarda: `Authorization: Bearer <access_token>`