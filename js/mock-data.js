/* Mock data — Поміч поруч MVP */
window.PP = window.PP || {};

PP.CITIES = ["Київ", "Львів", "Дніпро", "Одеса", "Харків"];

PP.DISTRICTS = {
  "Київ": ["Печерський", "Оболонський", "Подільський", "Шевченківський", "Солом'янський"],
  "Львів": ["Галицький", "Залізничний", "Сихівський"],
  "Дніпро": ["Центральний", "Самарський", "Шевченківський"],
  "Одеса": ["Приморський"],
};

PP.LANGUAGES = ["Українська", "Англійська", "Польська"];

PP.NAV = [
  { label: "Головна", href: "/" },
  { label: "Як це працює", href: "/how-it-works" },
  { label: "Каталог нянь", href: "/nanny/" },
  { label: "Блог", href: "/blog/" },
  { label: "FAQ", href: "/faq/" },
  { label: "Контакти", href: "/contacts" },
];

PP.HOW_IT_WORKS = [
  { step: 1, title: "Переглядайте або зареєструйтесь", desc: "Гості можуть шукати без акаунта. Батьки та помічники — окремі кабінети" },
  { step: 2, title: "Оберіть няню", desc: "Використовуйте фільтри та переглядайте профілі" },
  { step: 3, title: "Відкрийте контакти", desc: "Батьки оформлюють підписку для доступу до телефонів" },
  { step: 4, title: "Домовтесь", desc: "Спишіться в чаті про співбесіду онлайн або зустріч" },
];

PP.BENEFITS = [
  { icon: "🛡", title: "Перевірені профілі", desc: "Модерація документів кожної няні" },
  { icon: "🔒", title: "Безпечний пошук", desc: "GDPR та ЗУ про захист даних" },
  { icon: "👥", title: "Велика база", desc: "Сотні профілів у містах України" },
  { icon: "⚡", title: "Швидкий підбір", desc: "Знайдіть няню за лічені хвилини" },
];

function genAvail() {
  const d = {};
  const s = ["available", "busy", "vacation"];
  for (let i = 1; i <= 14; i++) {
    d[`2026-06-${String(i).padStart(2, "0")}`] = s[Math.floor(Math.random() * 3)];
  }
  return d;
}

PP.NANNIES = [
  {
    id: "1", name: "Олена Кovalenko", age: 32, city: "Київ", district: "Печерський",
    photo: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&h=400&fit=crop&crop=faces",
    rating: 4.9, reviewCount: 47, hourlyRate: 350, experienceYears: 8,
    description: "Досвідчена няня з педагогічною освітою. Люблю працювати з дітьми від 1 року.",
    certificates: ["Педагогічна освіта", "Курс першої допомоги"],
    languages: ["Українська", "Англійська"], hasCar: true, medicalEducation: false,
    firstAidCourse: true, availability: genAvail(), isVerified: true,
  },
  {
    id: "2", name: "Марія Петренко", age: 28, city: "Київ", district: "Оболонський",
    photo: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&h=400&fit=crop&crop=faces",
    rating: 4.7, reviewCount: 32, hourlyRate: 300, experienceYears: 5,
    description: "Енергійна та відповідальна. Спеціалізуюсь на дошкільнятах.",
    certificates: ["Медична сестра", "Montessori"],
    languages: ["Українська"], hasCar: false, medicalEducation: true,
    firstAidCourse: true, availability: genAvail(), isVerified: true,
  },
  {
    id: "3", name: "Анна Шевченко", age: 35, city: "Львів", district: "Галицький",
    photo: "https://images.unsplash.com/photo-1594744803329-e58b31de8bf5?w=400&h=400&fit=crop&crop=faces",
    rating: 5.0, reviewCount: 61, hourlyRate: 400, experienceYears: 12,
    description: "12 років досвіду. Працювала з дітьми з особливими потребами.",
    certificates: ["Дефектолог", "Перша допомога", "CPR"],
    languages: ["Українська", "Польська"], hasCar: true, medicalEducation: true,
    firstAidCourse: true, availability: genAvail(), isVerified: true,
  },
  {
    id: "4", name: "Ірина Мельник", age: 26, city: "Дніпро", district: "Центральний",
    photo: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=faces",
    rating: 4.5, reviewCount: 18, hourlyRate: 250, experienceYears: 3,
    description: "Молода, але відповідальна. Активні ігри та розвиваючі заняття.",
    certificates: ["Курс няні", "Перша допомога"],
    languages: ["Українська", "Англійська"], hasCar: false, medicalEducation: false,
    firstAidCourse: true, availability: genAvail(), isVerified: true,
  },
  {
    id: "5", name: "Наталія Бойко", age: 30, city: "Дніпро", district: "Самарський",
    photo: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=faces",
    rating: 4.8, reviewCount: 24, hourlyRate: 280, experienceYears: 6,
    description: "Догляд за дітьми від 6 місяців. Спокійна та уважна.",
    certificates: ["Медична освіта", "Курс няні"],
    languages: ["Українська"], hasCar: true, medicalEducation: true,
    firstAidCourse: true, availability: genAvail(), isVerified: true,
  },
  {
    id: "6", name: "Юлія Савченко", age: 27, city: "Львів", district: "Залізничний",
    photo: "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=400&h=400&fit=crop&crop=faces",
    rating: 4.6, reviewCount: 15, hourlyRate: 320, experienceYears: 4,
    description: "Творчі заняття, музика та розвиток мовлення.",
    certificates: ["Montessori", "Музична освіта"],
    languages: ["Українська", "Англійська", "Польська"], hasCar: false, medicalEducation: false,
    firstAidCourse: true, availability: genAvail(), isVerified: true,
  },
  {
    id: "7", name: "Софія Кравець", age: 31, city: "Одеса", district: "Приморський",
    photo: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=400&fit=crop&crop=faces",
    rating: 4.9, reviewCount: 29, hourlyRate: 340, experienceYears: 7,
    description: "Досвід проживання з сім'єю. Готування дитячого меню.",
    certificates: ["Курс няні", "Кулінарія для дітей"],
    languages: ["Українська", "Російська"], hasCar: true, medicalEducation: false,
    firstAidCourse: true, availability: genAvail(), isVerified: true,
  },
];

PP.REVIEWS = {
  "1": [
    { author: "Тетяна Б.", rating: 5, text: "Олена — чудова няня! Діти обожнюють.", date: "2026-05-20" },
    { author: "Андрій М.", rating: 5, text: "Професійний підхід, допомогла з режимом.", date: "2026-04-12" },
  ],
  "2": [{ author: "Оксана В.", rating: 5, text: "Марія чудово працює з дошкільнятами.", date: "2026-05-15" }],
  "3": [{ author: "Наталія С.", rating: 5, text: "Великий досвід з особливими потребами.", date: "2026-06-01" }],
  "4": [{ author: "Олег П.", rating: 5, text: "Ірина чудово займається з нашою донькою.", date: "2026-05-10" }],
  "5": [{ author: "Людмила К.", rating: 5, text: "Наталія дуже уважна до дітей.", date: "2026-05-22" }],
  "7": [{ author: "Ірина Д.", rating: 5, text: "Софія готує смачні страви для дітей.", date: "2026-06-05" }],
};

PP.FAQ = [
  { q: "Як працює платформа?", a: "Реєструєтесь, шукаєте няню, оформлюєте підписку та домовляєтесь через чат." },
  { q: "Чи перевіряються няні?", a: "Так, кожен профіль проходить модерацію документів адміністратором." },
  { q: "Які способи оплати?", a: "LiqPay, WayForPay та Fondy для підписок і відкриття контактів." },
  { q: "Чи можна скасувати підписку?", a: "Так, у будь-який момент у кабінеті батьків." },
];

PP.BLOG = [
  {
    slug: "yak-obraty-nyanyu", title: "Як обрати надійну няню: 7 порад",
    excerpt: "Практичний гайд для батьків", date: "2026-06-01", category: "Поради",
    image: "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=800&h=500&fit=crop",
    content: ["Перевіряйте рейтинг та відгуки.", "Звертайте увагу на сертифікати.", "Домовтесь про формат догляду заздалегідь."],
  },
  {
    slug: "bezpeka-ditey", title: "Безпека дітей перед наймом",
    excerpt: "Чек-лист документів", date: "2026-05-28", category: "Безпека",
    image: "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=800&h=500&fit=crop",
    content: ["Модерація профілів адміном.", "Перевірка паспорта та ІПН.", "Співбесіда очно або онлайн."],
  },
];

PP.PRICING = [
  { id: "single", title: "1 контакт", price: 50, desc: "Один помічник", featured: false },
  { id: "pack5", title: "5 контактів", price: 200, desc: "Пакет з 5 контактами", featured: true },
  { id: "city7", title: "Місто · 7 днів", price: 500, desc: "Усі контакти в місті", featured: false },
];

PP.PARENT_NAV = [
  { label: "Дашборд", href: PP.ROUTES.parentCabinet, icon: "📊" },
  { label: "Пошук", href: PP.ROUTES.parentSearch, icon: "🔍" },
  { label: "Профіль", href: PP.ROUTES.parentProfile, icon: "👤" },
  { label: "Обране", href: PP.ROUTES.parentFavorites, icon: "❤" },
  { label: "Чат", href: PP.ROUTES.parentChat, icon: "💬" },
  { label: "Платежі", href: PP.ROUTES.parentPayments, icon: "💳" },
  { label: "Відгуки", href: PP.ROUTES.parentReviews, icon: "⭐" },
];

PP.NANNY_NAV = [
  { label: "Дашборд", href: PP.ROUTES.nannyCabinet, icon: "📊" },
  { label: "Профіль", href: PP.ROUTES.nannyProfile, icon: "👤" },
  { label: "Календар", href: PP.ROUTES.nannyCalendar, icon: "📅" },
  { label: "Документи", href: PP.ROUTES.nannyDocuments, icon: "📄" },
  { label: "Повідомлення", href: PP.ROUTES.nannyMessages, icon: "💬" },
  { label: "Рейтинг", href: PP.ROUTES.nannyRating, icon: "⭐" },
];

PP.ADMIN_NAV = [
  { label: "Дашборд", href: PP.ROUTES.admin, icon: "📊" },
  { label: "Користувачі", href: PP.ROUTES.adminUsers, icon: "👥" },
  { label: "Профілі", href: PP.ROUTES.adminProfiles, icon: "🪪" },
  { label: "Документи", href: "/admin/documents", icon: "📄" },
  { label: "Повідомлення", href: PP.ROUTES.adminMessages, icon: "💬" },
  { label: "Контент", href: "/admin/content", icon: "📝" },
  { label: "Фінанси", href: PP.ROUTES.adminFinance, icon: "💰" },
  { label: "Аналітика", href: PP.ROUTES.adminAnalytics, icon: "📈" },
];

PP.getNanny = (id) => PP.NANNIES.find((n) => n.id === id);
PP.formatPrice = (n) => `${n} ₴`;
