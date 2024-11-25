#!/bin/bash

# تحديث الحزم
apt update && apt upgrade -y

# تثبيت المتطلبات الأساسية
pkg install python git -y

# استنساخ المشروع من GitHub
echo "⏳ جاري تنزيل المشروع من GitHub..."
git clone https://github.com/zeko1244/test ~/test

# الانتقال إلى مجلد المشروع
cd ~/test

# تثبيت المكتبات المطلوبة إذا كان هناك ملف requirements.txt
if [ -f "requirements.txt" ]; then
  echo "⏳ جاري تثبيت المكتبات المطلوبة..."
  pip install -r requirements.txt
else
  echo "📋 لا يوجد ملف requirements.txt لتثبيت المكتبات."
fi

# تشغيل البوت
if [ -f "snd.py" ]; then
  echo "✅ تم تثبيت البوت بنجاح!"
  python3 snd.py
else
  echo "❌ لم يتم العثور على الملف snd.py."
fi
