import os
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.content.models import BlogPost, FAQItem
from apps.core.models import SiteSettings
from apps.geo.models import City, District
from apps.nannies.models import AvailabilitySlot, NannyProfile
from apps.payments.models import PricingPlan

User = get_user_model()

CITIES = {
    "Київ": ["Печерський", "Оболонський", "Подільський", "Шевченківський", "Солом'янський"],
    "Львів": ["Галицький", "Залізничний", "Сихівський"],
    "Дніпро": ["Центральний", "Самарський", "Шевченківський"],
    "Одеса": ["Приморський"],
    "Харків": ["Шевченківський"],
}

NANNIES = [
    {
        "email": "olena.k@demo.pomich-poruch.com.ua",
        "first_name": "Олена",
        "last_name": "Kovalenko",
        "city": "Київ",
        "district": "Печерський",
        "photo_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&h=400&fit=crop&crop=faces",
        "rating": 4.9,
        "reviews": 47,
        "hourly": 350,
        "exp": 8,
        "age": 32,
        "desc": "Досвідчена няня з педагогічною освітою.",
        "certs": ["Педагогічна освіта", "Курс першої допомоги"],
        "langs": ["Українська", "Англійська"],
        "has_car": True,
        "medical": False,
        "first_aid": True,
    },
    {
        "email": "maria.p@demo.pomich-poruch.com.ua",
        "first_name": "Марія",
        "last_name": "Петренко",
        "city": "Київ",
        "district": "Оболонський",
        "photo_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&h=400&fit=crop&crop=faces",
        "rating": 4.7,
        "reviews": 32,
        "hourly": 300,
        "exp": 5,
        "age": 28,
        "desc": "Енергійна та відповідальна.",
        "certs": ["Медична сестра", "Montessori"],
        "langs": ["Українська"],
        "has_car": False,
        "medical": True,
        "first_aid": True,
    },
    {
        "email": "anna.s@demo.pomich-poruch.com.ua",
        "first_name": "Анна",
        "last_name": "Шевченко",
        "city": "Львів",
        "district": "Галицький",
        "photo_url": "https://images.unsplash.com/photo-1594744803329-e58b31de8bf5?w=400&h=400&fit=crop&crop=faces",
        "rating": 5.0,
        "reviews": 61,
        "hourly": 400,
        "exp": 12,
        "age": 35,
        "desc": "12 років досвіду.",
        "certs": ["Дефектолог", "Перша допомога", "CPR"],
        "langs": ["Українська", "Польська"],
        "has_car": True,
        "medical": True,
        "first_aid": True,
    },
    {
        "email": "iryna.m@demo.pomich-poruch.com.ua",
        "first_name": "Ірина",
        "last_name": "Мельник",
        "city": "Дніпро",
        "district": "Центральний",
        "photo_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=faces",
        "rating": 4.5,
        "reviews": 18,
        "hourly": 250,
        "exp": 3,
        "age": 26,
        "desc": "Молода, але відповідальна. Активні ігри та розвиваючі заняття.",
        "certs": ["Курс няні", "Перша допомога"],
        "langs": ["Українська", "Англійська"],
        "has_car": False,
        "medical": False,
        "first_aid": True,
    },
    {
        "email": "natalia.b@demo.pomich-poruch.com.ua",
        "first_name": "Наталія",
        "last_name": "Бойко",
        "city": "Дніпро",
        "district": "Самарський",
        "photo_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=faces",
        "rating": 4.8,
        "reviews": 24,
        "hourly": 280,
        "exp": 6,
        "age": 30,
        "desc": "Догляд за дітьми від 6 місяців. Спокійна та уважна.",
        "certs": ["Медична освіта", "Курс няні"],
        "langs": ["Українська"],
        "has_car": True,
        "medical": True,
        "first_aid": True,
    },
    {
        "email": "yulia.s@demo.pomich-poruch.com.ua",
        "first_name": "Юлія",
        "last_name": "Савченко",
        "city": "Львів",
        "district": "Залізничний",
        "photo_url": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=400&h=400&fit=crop&crop=faces",
        "rating": 4.6,
        "reviews": 15,
        "hourly": 320,
        "exp": 4,
        "age": 27,
        "desc": "Творчі заняття, музика та розвиток мовлення.",
        "certs": ["Montessori", "Музична освіта"],
        "langs": ["Українська", "Англійська", "Польська"],
        "has_car": False,
        "medical": False,
        "first_aid": True,
    },
    {
        "email": "sofia.k@demo.pomich-poruch.com.ua",
        "first_name": "Софія",
        "last_name": "Кравець",
        "city": "Одеса",
        "district": "Приморський",
        "photo_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=400&fit=crop&crop=faces",
        "rating": 4.9,
        "reviews": 29,
        "hourly": 340,
        "exp": 7,
        "age": 31,
        "desc": "Досвід проживання з сім'єю. Готування дитячого меню.",
        "certs": ["Курс няні", "Кулінарія для дітей"],
        "langs": ["Українська", "Російська"],
        "has_car": True,
        "medical": False,
        "first_aid": True,
    },
]


class Command(BaseCommand):
    help = "Seed demo data for Поміч поруч"

    def handle(self, *args, **options):
        self._seed_cities()
        self._seed_plans()
        self._seed_faq()
        self._seed_blog()
        self._seed_site_settings()
        self._seed_nannies()
        self._seed_admin()
        self.stdout.write(self.style.SUCCESS("Demo data seeded."))

    def _seed_cities(self):
        for idx, (city_name, districts) in enumerate(CITIES.items()):
            city, _ = City.objects.get_or_create(
                slug=city_name.lower().replace("'", ""),
                defaults={"name": city_name, "sort_order": idx},
            )
            for dname in districts:
                District.objects.get_or_create(
                    city=city,
                    slug=dname.lower().replace("'", "")[:48],
                    defaults={"name": dname},
                )

    def _seed_plans(self):
        plans = [
            ("single", "1 контакт", 50, "Один помічник", PricingPlan.PlanType.SINGLE, 1, 0, False),
            ("pack5", "5 контактів", 200, "Пакет з 5 контактами", PricingPlan.PlanType.PACK5, 5, 0, True),
            ("city7", "Місто · 7 днів", 500, "Усі контакти в місті", PricingPlan.PlanType.CITY7, 0, 7, False),
        ]
        for code, title, price, desc, ptype, contacts, days, featured in plans:
            PricingPlan.objects.update_or_create(
                code=code,
                defaults={
                    "title": title,
                    "price_uah": price,
                    "description": desc,
                    "plan_type": ptype,
                    "contact_limit": contacts,
                    "city_access_days": days,
                    "is_featured": featured,
                    "is_active": True,
                },
            )

    def _seed_faq(self):
        items = [
            ("Як працює платформа?", "Реєструєтесь, шукаєте няню, оформлюєте підписку та домовляєтесь через чат."),
            ("Чи перевіряються няні?", "Так, кожен профіль проходить модерацію документів адміністратором."),
            ("Які способи оплати?", "LiqPay, WayForPay та Fondy для підписок і відкриття контактів."),
            ("Чи можна скасувати підписку?", "Так, у будь-який момент у кабінеті батьків."),
        ]
        for i, (q, a) in enumerate(items):
            FAQItem.objects.update_or_create(question=q, defaults={"answer": a, "sort_order": i})

    def _seed_blog(self):
        BlogPost.objects.update_or_create(
            slug="yak-obraty-nyanyu",
            defaults={
                "title": "Як обрати надійну няню: 7 порад",
                "excerpt": "Практичний гайд для батьків",
                "category": "Поради",
                "image_url": "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=800&h=500&fit=crop",
                "content": [
                    "Перевіряйте рейтинг та відгуки.",
                    "Звертайте увагу на сертифікати.",
                    "Домовтесь про формат догляду заздалегідь.",
                ],
                "is_published": True,
                "published_at": date(2026, 6, 1),
            },
        )
        BlogPost.objects.update_or_create(
            slug="bezpeka-ditey",
            defaults={
                "title": "Безпека дітей перед наймом",
                "excerpt": "Чек-лист документів",
                "category": "Безпека",
                "image_url": "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=800&h=500&fit=crop",
                "content": [
                    "Модерація профілів адміном.",
                    "Перевірка паспорта та ІПН.",
                    "Співбесіда очно або онлайн.",
                ],
                "is_published": True,
                "published_at": date(2026, 5, 28),
            },
        )

    def _seed_site_settings(self):
        SiteSettings.objects.update_or_create(
            pk=1,
            defaults={
                "site_name": "Поміч поруч",
                "support_email": "info@pomich-poruch.com.ua",
                "support_phone": "+380 44 123 45 67",
                "instagram_url": "https://www.instagram.com/pomich.poruch/",
                "facebook_url": "https://www.facebook.com/pomich.poruch/",
                "tiktok_url": "https://www.tiktok.com/@pomich.poruch",
                "meta_description": "Маркетплейс пошуку нянь в Україні",
            },
        )

    def _seed_nannies(self):
        for item in NANNIES:
            city = City.objects.get(name=item["city"])
            district = District.objects.filter(city=city, name=item["district"]).first()
            user, created = User.objects.get_or_create(
                email=item["email"],
                defaults={
                    "username": item["email"].split("@")[0],
                    "role": User.Role.NANNY,
                    "status": User.Status.ACTIVE,
                    "phone": "+380671234567",
                },
            )
            if created:
                user.set_password("DemoPassword123!")
                user.save()
            birth = date.today().replace(year=date.today().year - item["age"])
            profile, _ = NannyProfile.objects.update_or_create(
                user=user,
                defaults={
                    "first_name": item["first_name"],
                    "last_name": item["last_name"],
                    "birth_date": birth,
                    "city": city,
                    "district": district,
                    "photo_url": item["photo_url"],
                    "description": item["desc"],
                    "hourly_rate": item["hourly"],
                    "experience_years": item["exp"],
                    "languages": item["langs"],
                    "certificates": item["certs"],
                    "has_car": item["has_car"],
                    "medical_education": item["medical"],
                    "first_aid_course": item["first_aid"],
                    "is_verified": True,
                    "moderation_status": NannyProfile.ModerationStatus.APPROVED,
                    "rating_avg": item["rating"],
                    "review_count": item["reviews"],
                },
            )
            profile.availability.all().delete()
            for i in range(14):
                slot_date = date.today() + timedelta(days=i)
                AvailabilitySlot.objects.create(
                    nanny=profile,
                    date=slot_date,
                    status=AvailabilitySlot.Status.AVAILABLE if i % 3 else AvailabilitySlot.Status.BUSY,
                )

    def _seed_admin(self):
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@pomich-poruch.com.ua")
        password = os.environ.get("ADMIN_PASSWORD", "AdminPassword123!")
        base_username = admin_email.split("@")[0].replace(".", "_")[:140]

        user = User.objects.filter(email__iexact=admin_email).first()
        if user:
            user.role = User.Role.ADMIN
            user.status = User.Status.ACTIVE
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            return

        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{suffix}"
            suffix += 1

        User.objects.create_user(
            username=username,
            email=admin_email,
            password=password,
            role=User.Role.ADMIN,
            status=User.Status.ACTIVE,
            is_staff=True,
            is_superuser=True,
        )
