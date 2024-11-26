#!/bin/bash

# تحديث Termux وتثبيت الحزم الأساسية
pkg update && pkg upgrade -y
pkg install python git -y

# استنساخ المستودع
git clone https://github.com/zeko1244/test.git
cd test

# تثبيت المكتبات المطلوبة
pip install -r requirements.txt

# تشغيل البرنامج
python snd.py
