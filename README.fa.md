[**English**](README.md) | **فارسی**

# گردآورنده کانفیگ

یک جمع‌آوری‌کننده حرفه‌ای و گزینش‌شده اشتراک V2Ray/VLESS/Trojan/ShadowSocks.

**فلسفه:** این یک انبار عظیم کانفیگ نیست. این یک تولیدکننده اشتراک سبک و گزینش‌شده است که فقط کانفیگ‌های باکیفیت را جمع‌آوری، امتیازدهی و منتشر می‌کند.

## ویژگی‌ها

- جمع‌آوری کانفیگ از کانال‌های عمومی تلگرام، مخازن گیت‌هاب و URLهای اشتراک
- تجزیه vmess://, vless://, trojan:// و ss://
- حذف تکراری هوشمند (بر اساس پروتکل + هاست + پورت + رمز + ترنسپورت)
- امتیازدهی کانفیگ‌ها (Reality +25، Cloudflare +20، TLS +15 و ...)
- اجرای چک سلامت TCP سبک (3 ثانیه، ناهمگام)
- تولید 6 خروجی دسته‌بندی‌شده: mix، cloudflare، reality، mobile، fast، clean
- خروجی به صورت .txt خام، base64 و Clash YAML (اختیاری)
- کاملاً ناهمگام (asyncio + httpx + telethon)
- بدون دیتابیس — کش سبک JSON
- استقرار آسان: GitHub Actions، داکر، کرون VPS

## معماری

```
app/
  collectors/       # جمع‌آوری‌کننده‌های تلگرام، گیت‌هاب و URL اشتراک
  extractors/       # استخراج لینک با regex
  parsers/          # تجزیه‌کننده‌های vmess, vless, trojan, shadowsocks
  normalizers/      # نرمال‌سازی کانفیگ (هاست، ترنسپورت و ...)
  scoring/          # موتور امتیازدهی
  health/           # چک سلامت TCP ناهمگام
  filters/          # فیلترهای دسته‌بندی (mix, cf, reality, mobile, fast, clean)
  outputs/          # تولید خروجی خام، base64 و Clash YAML
  models/           # مدل Pydantic ProxyConfig
  utils/            # لاگر، تلاش مجدد، کش
  pipeline.py       # هماهنگ‌کننده پایپلاین
  sources.py        # بارگذاری منابع
config/             # فایل‌های تنظیمات
generated/          # اشتراک‌های تولیدشده
```

## شروع سریع

```bash
# نصب وابستگی‌ها
pip install -r requirements.txt

# افزودن منابع (توضیح در ادامه)
# سپس اجرا
python main.py
```

## افزودن منابع

### کانال‌های تلگرام

فایل `config/telegram_channels.txt` را ویرایش کنید:

```
@freev2ray
@proxy_channel
```

نیاز به TG_API_ID و TG_API_HASH از https://my.telegram.org دارد.

### گیت‌هاب / URLهای خام

فایل `config/github_sources.json` را ویرایش کنید:

```json
[
  {
    "name": "my-source",
    "url": "https://raw.githubusercontent.com/user/repo/main/configs.txt",
    "type": "raw"
  }
]
```

### URLهای اشتراک

فایل `config/subscription_sources.txt` را ویرایش کنید:

```
https://example.com/subscription
https://another.example.com/config
```

اشتراک‌های رمزگذاری‌شده با base64 به طور خودکار تشخیص داده می‌شوند.

## متغیرهای محیطی

| متغیر | الزامی | توضیحات |
|----------|----------|-------------|
| `TG_API_ID` | برای تلگرام | شناسه API تلگرام (https://my.telegram.org) |
| `TG_API_HASH` | برای تلگرام | هش API تلگرام |
| `TG_SESSION` | خیر | نام نشست Telethon (پیش‌فرض: anon) |
| `GITHUB_TOKEN` | خیر | توکن گیت‌هاب برای محدودیت نرخ بیشتر |

## استقرار

### GitHub Actions

1. این مخزن را fork کنید
2. `TG_API_ID` و `TG_API_HASH` را به GitHub Secrets اضافه کنید
3. workflow هر 10 دقیقه به طور خودکار اجرا می‌شود

### داکر

```bash
docker-compose up -d
```

### کرون VPS

```bash
# اجرا هر 10 دقیقه
*/10 * * * * cd /path/to/config-collector && python3 main.py >> /var/log/collector.log 2>&1
```

## خروجی‌ها

پس از اجرا، پوشه `generated/` شامل موارد زیر است:

| فایل | توضیحات | حداکثر کانفیگ |
|------|---------|---------------|
| `mix.txt` | بهترین کانفیگ‌های کلی | 300 |
| `cloudflare.txt` | فقط Cloudflare CDN | 150 |
| `reality.txt` | فقط Reality/XTLS/Vision | 100 |
| `mobile.txt` | مناسب موبایل | 100 |
| `fast.txt` | بالاترین امتیاز | 50 |
| `clean.txt` | کانفیگ‌های تمیز | 100 |
| `base64/*.txt` | نسخه رمزگذاری‌شده base64 | همان |

## تنظیمات

فایل `config/settings.yaml` را برای تمام تنظیمات ببینید:

- محدودیت خروجی هر دسته
- زمان‌های انتظار (HTTP، TCP)
- همروندی چک سلامت
- فعال/غیرفعال کردن منابع
- تنظیمات تلاش مجدد
- سطح/فرمت لاگینگ
- تنظیمات فرمت خروجی (خام، base64، clash)

## مجوز

MIT
