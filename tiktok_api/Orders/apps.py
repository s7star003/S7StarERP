from django.apps import AppConfig
import os
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

class OrdersConfig(AppConfig):
    name = 'Tiktok_api.Orders'

    def ready(self):
        # 避免重复执行
        if os.environ.get('RUN_MAIN', None) != 'true':
            return
        try:
            from Tiktok_api.Auth.RefreshToken import refresh_token_main
            print("[INFO] 正在自动刷新 TikTok token ...")
            refresh_token_main()
            print("[INFO] TikTok token 自动刷新完成")

            # 启动定时任务，每天0点自动刷新
            scheduler = BackgroundScheduler()
            scheduler.add_job(refresh_token_main, 'cron', hour=0, minute=0)
            scheduler.start()
            print("[INFO] 已启动每日0点自动刷新 TikTok token 的定时任务")
            atexit.register(lambda: scheduler.shutdown())
        except Exception as e:
            print(f"[WARN] 启动时自动刷新 TikTok token 失败: {e}")
