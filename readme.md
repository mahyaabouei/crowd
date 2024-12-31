
### راه‌اندازی مجدد سرویس

```bash
sudo systemctl restart crowd
```

### متوقف کردن سرویس

```bash
sudo systemctl stop crowd
```

### شروع سرویس

```bash
sudo systemctl start crowd
```


```bash
sudo systemctl status crowd
sudo systemctl restart crowd
```

```bash
sudo journalctl -u crowd -f
```


```bash
sudo systemctl show -p ActiveState -p LoadState -p MemoryCurrent -p MemoryMax crowd
ps aux | grep crowd
sudo netstat -tulpn | grep crowd

```

### مسیرهای مهم
- فایل سرویس: `/etc/systemd/system/crowd.service`
- لاگ‌های سیستمی: `/var/log/syslog`
- فایل پیکربندی: `/etc/crowd/crowd.conf`
- فایل پیکربندی سیستمی: `/etc/crowd/crowd-init.d/crowd-init.conf`
- فایل پیکربندی سیستمی: `/etc/crowd/crowd-init.d/crowd-init.conf`
- فایل پیکربندی سیستمی: `/etc/crowd/crowd-init.d/crowd-init.conf`
- فایل پیکربندی سیستمی: `/etc/crowd/crowd-init.d/crowd-init.conf`


