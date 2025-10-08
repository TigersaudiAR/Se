# TwoCards Platform Backend

منصة TwoCards عبارة عن واجهة برمجية متكاملة مبنية بواسطة FastAPI و SQLModel لإدارة المنتجات الرقمية، الأكواد، التكامل مع منصة زد، الذكاء الاصطناعي، الرسائل الفورية، وتسجيل الأحداث.

## المتطلبات

- Python 3.12
- Poetry لإدارة الحزم
- قاعدة بيانات PostgreSQL (أو SQLite للتطوير)

## الإعداد السريع

```bash
cd backend
poetry lock          # في حال تعديل التبعيات
poetry install       # تنصيب المتطلبات
poetry run uvicorn app.main:app --reload
```

> **ملاحظة:** في البيئات المعزولة قد يلزم تنفيذ `poetry lock` محليًا قبل `poetry install` بسبب الحاجة إلى تحميل بيانات الحزم.

## المتغيرات الأساسية

- `ZID_TOKEN`
- `OPENAI_API_KEY`
- `WA_TOKEN`
- `WA_PHONE_ID`
- `EMAIL_TOKENS`
- `ENCRYPTION_SECRET`

توفر الواجهة النهائية نقاط وصول متكاملة لإدارة المستخدمين، المنتجات، الأكواد، السجلات، الإعدادات، الذكاء الاصطناعي، واتساب، والدردشة الداخلية.
