@echo off
echo Stopping Telegram Bot on DigitalOcean server...
echo.
echo Server: 64.225.20.106
echo ========================================
echo.

echo Stopping telegram-bot systemd service...
ssh -i "C:\Users\tuan\.ssh\digital_ocean_openssh_key" root@64.225.20.106 "systemctl stop telegram-bot.service"

echo.
echo Checking service status...
ssh -i "C:\Users\tuan\.ssh\digital_ocean_openssh_key" root@64.225.20.106 "systemctl status telegram-bot.service --no-pager | head -3"

echo.
echo Checking for remaining bot processes...
ssh -i "C:\Users\tuan\.ssh\digital_ocean_openssh_key" root@64.225.20.106 "ps aux | grep -E '/root/telegram-bot/bot.py' | grep -v grep || echo 'All bot processes stopped successfully'"

echo.
echo ========================================
echo Bot stopping complete.
echo.
pause