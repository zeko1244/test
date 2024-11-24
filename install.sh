
#!/bin/bash

# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Python والمكتبات المطلوبة
sudo apt install -y python3 python3-pip git
pip3 install -r requirements.txt

echo "✔️ تم تثبيت المتطلبات بنجاح."
