1. Mahsulotlar Moduli (Products)

Bu bo‘lim xaridorlar mahsulotlarni ko‘rishi va qidirishi uchun xizmat qiladi.

    GET /api/products/ — Barcha mahsulotlar ro‘yxati (filtrlash va qidiruv bilan).

    GET /api/products/<id>/ — Bitta mahsulot haqida to‘liq ma’lumot.

    GET /api/categories/ — Kategoriyalar ro‘yxati (maishiy texnika, kiyim-kechak va h.k.).

    GET /api/categories/<id>/products/ — Ma’lum bir kategoriyaga tegishli mahsulotlar.

2. Foydalanuvchilar va Autentifikatsiya (Users & Auth)

Xaridorlar profilini boshqarishi va buyurtma berishi uchun kerak.

    POST /api/auth/register/ — Ro‘yxatdan o‘tish.

    POST /api/auth/login/ — Tizimga kirish (Token olish).

    GET /api/users/me/ — Foydalanuvchining shaxsiy ma’lumotlari (profil).

    PUT /api/users/me/update/ — Profil ma’lumotlarini tahrirlash.

3. Savat va Sevimlilar (Cart & Wishlist)

Xaridor sotib olmoqchi bo‘lgan narsalarini saqlab turishi uchun.

    GET /api/cart/ — Savatdagi mahsulotlar ro‘yxati.

    POST /api/cart/add/ — Savatga mahsulot qo‘shish.

    DELETE /api/cart/remove/<id>/ — Savatdan mahsulotni o‘chirish.

    POST /api/wishlist/toggle/ — Mahsulotni "yoqdi" (like) qilish yoki bekor qilish.

4. Buyurtmalar Moduli (Orders)

Loyiha "Market" bo‘lishi uchun eng muhim qism.

    POST /api/orders/create/ — Buyurtma berish (savatdagi narsalarni rasmiylashtirish).

    GET /api/orders/my-orders/ — Foydalanuvchining avvalgi buyurtmalari tarixi.

    GET /api/orders/<id>/ — Muayyan buyurtmaning holati (yetkazib berilmoqda, bajarildi va h.k.).

5. Qo'shimcha (Review & Rating)

    POST /api/products/<id>/review/ — Mahsulotga izoh qoldirish va yulduzcha (reiting) berish.