from scholarly import scholarly, ProxyGenerator
import json
from datetime import datetime
import os

# 1. 检查环境变量是否正确读取
scholar_id = os.environ.get('GOOGLE_SCHOLAR_ID')
if not scholar_id:
    print("❌ 错误: 未找到环境变量 GOOGLE_SCHOLAR_ID。请确保已正确设置。")
    exit(1)

print("正在配置代理网络 (这可能需要几十秒来寻找可用的免费代理)...")
# 2. 设置代理以绕过 Google 的反爬虫限制
pg = ProxyGenerator()
# 调用你之前安装的 free-proxy
success = pg.FreeProxies() 
if not success:
    print("⚠️ 警告: 无法获取有效的免费代理，尝试直连...")
else:
    scholarly.use_proxy(pg)
    print("✅ 代理配置成功！")

try:
    print(f"正在向 Google Scholar 发送请求寻找作者 (ID: {scholar_id})...")
    # 这步获取基础信息
    author: dict = scholarly.search_author_id(scholar_id)
    print("✅ 成功找到作者！正在抓取详细文献和引用数据 (这步耗时最长)...")
    
    # 这步会发送大量请求来填充所有文献
    scholarly.fill(author, sections=['basics', 'indices', 'counts', 'publications'])
    print("✅ 数据抓取完成！")

except Exception as e:
    print(f"❌ 抓取过程中发生错误或被 Google 拦截: {e}")
    exit(1)

# 处理和保存数据
name = author.get('name', 'Unknown')
author['updated'] = str(datetime.now())
author['publications'] = {v['author_pub_id']:v for v in author.get('publications', [])}

print("正在保存数据...")
os.makedirs('results', exist_ok=True)

# 保存完整数据
with open(f'results/gs_data.json', 'w', encoding='utf-8') as outfile:
    json.dump(author, outfile, ensure_ascii=False, indent=2)

# 保存 Shields.io 徽章数据
shieldio_data = {
  "schemaVersion": 1,
  "label": "citations",
  "message": f"{author.get('citedby', 0)}",
}
with open(f'results/gs_data_shieldsio.json', 'w', encoding='utf-8') as outfile:
    json.dump(shieldio_data, outfile, ensure_ascii=False)

print(f"🎉 运行结束！成功保存 {name} 的引用数据: {author.get('citedby', 0)} 次。")