1. Foydalanuvchi va Do'kon Tizimi
User (Foydalanuvchilar)

Bu jadval tizimdagi barcha foydalanuvchilarni saqlaydi.

    user_id: Takrorlanmas kalit (Primary Key).

    phone: Yetkazib berish va mijoz bilan bog‘lanish uchun eng muhim ustun. NotNull.

    is_active, is_staff, is_admin: Foydalanuvchi turini (mijoz, do‘kon egasi yoki tizim admini) ajratish uchun.

Shop (Do'konlar)

Sotuvchilarning ma’lumotlari.

    user_id: Do‘kon qaysi foydalanuvchiga tegishli ekanligini bog‘laydi (Foreign Key).

    rating: Do‘konning umumiy reytingi.

2. Mahsulotlar va Chegirmalar (Eng muhim qism)
Item (Mahsulotlar)

Har bir mahsulotning asosiy ma’lumotlari va narxlari.

    price: Mahsulotning hozirgi (sotiladigan) narxi.

    old_price: Mahsulotning chegirmadan oldingi narxi. Nullable: True (Aksiya yo‘q bo‘lsa bo‘sh qoladi).

    discount_id: Agar mahsulot guruhli (ommaviy) aksiyaga bog‘lansa, shu yerga ID yoziladi. Nullable: True.

Discount (Aksiyalar)

Guruhli chegirmalar kampaniyasi (masalan, "Yozgi chegirmalar - 20%").

    percent: Chegirma miqdori (foizda).

    start_date, end_date: Aksiyaning amal qilish vaqti.

    is_active: Boolean bayroq. Agar aksiya muddati tugasa yoki o'chirilsa, unga bog'langan barcha mahsulotlar asl narxiga qaytadi.

3. Savat va Buyurtmalar
Order (Buyurtma)

Mijozning yakuniy xaridi.

    location_id: Mijoz mahsulotni qaysi punktidan olib ketishini belgilaydi (DeliveryPunktga bog'lanadi).

    promokod_id: Ishlatilgan promokod. Nullable: True.

    status: Buyurtmaning hozirgi holati (Yangi, Yo'lda, Yakunlandi).

OrderItem (Buyurtma tarkibi)

Buyurtma ichidagi har bir mahsulotning tarixi.

    price_snapshot: Buyurtma berilgan lahzadagi yakuniy narx.

        Nega kerak? Keyinchalik mahsulot narxi o'zgarsa yoki aksiya tugasa ham, buyurtma tarixida mijoz necha pulga sotib olgani o'zgarmasdan qoladi.

4. Yetkazib berish va Qo'shimcha Jadvallar

    DeliveryPunkt: Mahsulotlar yetkaziladigan punktlar ro‘yxati.

    Promokod: Umumiy buyurtma summasiga chegirma beruvchi kodlar. usage_limit necha marta ishlatish mumkinligini belgilaydi.

    Comment: Mijozlar fikri. description Nullable: True bo‘lishi mumkin (mijoz matn yozmasdan shunchaki reyting qo‘yishi mumkin).

    Bucket va ItemBucket: Mijoz mahsulotlarni buyurtma qilishdan oldin yig‘ib turadigan savat tizimi.

Jadvallararo Bog'liqlik Mantiqi (Process Flow)

    Aksiya yaratish: Do'kon egasi Discount yaratadi (masalan, 15%).

    Mahsulotga biriktirish: Kerakli mahsulotlarning discount_id ustuniga shu aksiyani bog'laydi.

    Narx hisoblash: Backend kodida Item.priceni Discount.percentga ko'paytirib, yangi narx foydalanuvchiga ko'rsatiladi.

    Individual chegirma: Agar umumiy aksiya bo'lmasa, do'kon egasi shunchaki old_priceni to'ldirib, priceni arzonlashtirib qo'yadi.

    Buyurtma: Mijoz punktni (location_id) tanlaydi va buyurtma beradi. To‘lov holati Payment jadvalida aks etadi.
    