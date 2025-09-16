@echo off
echo Deploying Telegram Bot to DigitalOcean...
echo.
echo Server: 64.225.20.106
echo ========================================
echo.

echo Step 1: Stopping current bot service...
ssh -i "C:\Users\tuan\.ssh\digital_ocean_openssh_key" root@64.225.20.106 "systemctl stop telegram-bot.service"

echo.
echo Step 2: Pulling latest code from Git...
ssh -i "C:\Users\tuan\.ssh\digital_ocean_openssh_key" root@64.225.20.106 "cd /root/telegram-bot && git pull origin master"

echo.
echo Step 3: Installing/updating dependencies...
ssh -i "C:\Users\tuan\.ssh\digital_ocean_openssh_key" root@64.225.20.106 "cd /root/telegram-bot && source venv/bin/activate && pip install -r requirements.txt"

echo.
echo Step 4: Starting bot service...
ssh -i "C:\Users\tuan\.ssh\digital_ocean_openssh_key" root@64.225.20.106 "systemctl start telegram-bot.service"

echo.
echo Step 5: Checking service status...
ssh -i "C:\Users\tuan\.ssh\digital_ocean_openssh_key" root@64.225.20.106 "systemctl status telegram-bot.service --no-pager | head -5"

echo.
echo Step 6: Checking bot processes...
ssh -i "C:\Users\tuan\.ssh\digital_ocean_openssh_key" root@64.225.20.106 "ps aux | grep -E '/root/telegram-bot/bot.py' | grep -v grep || echo 'No bot processes found'"

echo.
echo ========================================
echo Deployment complete!
echo.
pause