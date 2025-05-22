from django.core.management.base import BaseCommand
from testapp.models import Drink

class Command(BaseCommand):
    help = '匯入飲料資料到資料庫'

    def handle(self, *args, **options):
        # 首先清空現有的飲料資料
        Drink.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('已清空現有的飲料資料'))
        
        # 定義要匯入的飲料資料
        drinks_data = [
            # 茶類
            {
                'name': '春烏龍',
                'category': 'tea',
                'description': '輕發酵，順口見長，茶香細膩。',
                'image_url': 'https://cc.tvbs.com.tw/img/program/upload/2024/07/04/20240704180740-d4079f88.jpg'
            },
            {
                'name': '輕烏龍',
                'category': 'tea',
                'description': '1 分火，口感溫潤，淡雅清香。',
                'image_url': 'https://www.niusnews.com/upload/imgs/default/202305_JEN/dejengoolongtea/5.jpg'
            },
            {
                'name': '焙烏龍',
                'category': 'tea',
                'description': '3分火，入口生津，醇厚甘潤。',
                'image_url': 'https://www.niusnews.com/upload/imgs/default/202305_JEN/dejengoolongtea/1.jpg'
            },
            
            # 奶類
            {
                'name': '黃金珍珠奶綠',
                'category': 'milk',
                'description': '得正「黃金珍珠奶綠」以香醇的奶綠為基底，搭配 Q 彈的黃金珍珠，黃金珍珠以黑糖蜜製，呈現誘人的金黃色澤，口感軟 Q 香甜，與奶綠的濃郁茶香完美融合，身為珍奶控的你一定不能錯過這款經典不敗選擇。',
                'image_url': 'https://blog-cdn.roo.cash/blog/wp-content/uploads/2024/06/%E9%BB%83%E9%87%91%E7%8F%8D%E7%8F%A0%E5%A5%B6%E7%B6%A0.jpg'
            },
            {
                'name': '烘吉鮮奶',
                'category': 'milk',
                'description': '得正新推出的焙茶 HOJICHA 系列掀起一波風潮。得正「烘吉鮮奶」選用日本靜岡秋番茶以慢火焙炒，直到散發出焙茶的迷人香氣，再加入鮮奶，鮮乳香氣揉合茶香，交織出豐富、滑順的口感，非常值得一試！',
                'image_url': 'https://cms.dejeng.com/wp-content/uploads/2024/01/231205-%E7%83%98%E5%90%89%E8%8C%B6%E6%96%B0%E5%93%81%E7%9B%B8%E9%97%9C%E8%B2%BC%E6%96%87_%E7%B6%B2%E9%A0%81-scaled.jpg'
            },
            {
                'name': '焙烏龍鮮奶',
                'category': 'milk',
                'description': '得正的「焙烏龍鮮奶」以招牌焙烏龍茶為基底，加入濃醇鮮奶調製而成，茶香與奶香完美融合，完全不會覺得膩口，整體口感滑順，如果喜歡茶味大於奶味的朋友，網友大推搭配茶凍一起！增加口感與味道層次，多重享受！',
                'image_url': 'https://images-tw.girlstyle.com/wp-content/uploads/2023/04/595fb951.jpeg?auto=format&w=1053'
            },
            
            # 其他
            {
                'name': '甘蔗春烏龍',
                'category': 'other',
                'description': '得正的「甘蔗春烏龍」以清爽的春烏龍為基底，加入新鮮甘蔗汁，甘蔗的清甜與春烏龍的淡雅茶香完美融合，口感清爽甘甜，帶有自然的甘蔗香氣，非常適合炎炎夏日來上一口，清涼又消暑！',
                'image_url': 'https://blog-cdn.roo.cash/blog/wp-content/uploads/2024/06/%E7%94%98%E8%94%97%E6%98%A5%E7%83%8F%E9%BE%8D.jpg'
            },
            {
                'name': '優酪春烏龍',
                'category': 'other',
                'description': '這杯是得正的人氣代表！許多人第一眼看去都會誤會成「優格」，這杯「優酪春烏龍」（55元，中杯、65元，大杯）並不是優格，而是葡萄柚、乳酸飲料加上春烏龍的組合，葡萄柚是現榨的，因此能喝到些許果肉，茶香與酸甜果香完美結合，清爽到不行，是夏天許多人的救贖手搖飲首選，建議點微糖、無糖即可。',
                'image_url': 'https://tristaliu.com/wp-content/uploads/2022/11/oolong-tea-project-2.jpeg'
            },
            {
                'name': '檸檬春烏龍',
                'category': 'other',
                'description': '「檸檬春烏龍」（50元，中杯、60元，大杯），也水果控很愛的夏日夯品。口感偏酸，但對於喜歡酸感的飲料人來說正好是完美酸度，檸檬加烏龍茶順口不澀，怕酸的朋友也可以選無糖、一分糖，酸度比較剛好，消暑解膩大推。',
                'image_url': 'https://images-tw.girlstyle.com/wp-content/uploads/2023/04/e156803f.jpeg?auto=format&w=1053'
            },
        ]
        
        # 將飲料資料匯入資料庫
        for drink_data in drinks_data:
            Drink.objects.create(**drink_data)
        
        self.stdout.write(self.style.SUCCESS(f'成功匯入 {len(drinks_data)} 筆飲料資料')) 