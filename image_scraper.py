import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import time
import random

def get_desktop_path():
    """获取桌面路径"""
    return os.path.join(os.path.expanduser("~"), "Desktop")

def get_image_urls(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.google.com/'
    }
    
    try:
        # 添加随机延迟
        time.sleep(random.uniform(1, 3))
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        
        # 检查是否是图片网站
        if 'pexels.com' in url:
            print("检测到 Pexels 网站，使用特殊处理...")
            # 这里可以添加针对 Pexels 的特殊处理
            # 例如使用他们的 API 或特定的选择器
            return []
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        image_tags = soup.find_all('img')
        image_urls = []
        
        # 获取基础URL
        base_url = urlparse(url)
        base_scheme = base_url.scheme or 'https'
        base_netloc = base_url.netloc
        
        for img in image_tags:
            img_url = img.get('src') or img.get('data-src')
            if img_url:
                # 处理以 // 开头的URL
                if img_url.startswith('//'):
                    img_url = f"{base_scheme}:{img_url}"
                # 处理相对URL
                elif not urlparse(img_url).netloc:
                    img_url = urljoin(url, img_url)
                # 过滤掉小图标和无效图片
                if not any(x in img_url.lower() for x in ['icon', 'logo', 'avatar']):
                    image_urls.append(img_url)
        
        return list(set(image_urls))  # 去重
        
    except requests.exceptions.RequestException as e:
        print(f"获取网页失败: {e}")
        print("可能的原因：")
        print("1. 网站有反爬虫机制")
        print("2. 网络连接问题")
        print("3. 网站需要登录")
        print("\n建议：")
        print("1. 尝试使用其他网站")
        print("2. 检查网络连接")
        print("3. 如果网站需要登录，请先登录后再使用")
        return []

def download_image(img_url, folder, index):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.google.com/'
    }
    
    try:
        # 添加随机延迟
        time.sleep(random.uniform(0.5, 1.5))
        
        # 处理URL中的特殊字符
        img_url = img_url.replace(' ', '%20')
        
        resp = requests.get(img_url, headers=headers, stream=True, timeout=15)
        resp.raise_for_status()
        
        # 获取文件扩展名
        content_type = resp.headers.get('content-type', '')
        if 'image' not in content_type:
            print(f"跳过非图片文件: {img_url}")
            return False
            
        ext = os.path.splitext(urlparse(img_url).path)[1]
        if not ext or ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            ext = '.jpg'
            
        filename = f"img_{str(index).zfill(3)}{ext}"
        filepath = os.path.join(folder, filename)
        
        # 避免重名
        count = 1
        while os.path.exists(filepath):
            filename = f"img_{str(index).zfill(3)}_{count}{ext}"
            filepath = os.path.join(folder, filename)
            count += 1
            
        with open(filepath, 'wb') as f:
            for chunk in resp.iter_content(8192):
                if chunk:
                    f.write(chunk)
        return True
        
    except Exception as e:
        print(f"下载失败: {img_url}")
        print(f"错误信息: {str(e)}")
        return False

def main():
    print("=" * 50)
    print("网页图片批量下载工具")
    print("=" * 50)
    print("注意：某些网站可能有反爬虫机制，可能无法正常下载")
    print("建议使用普通网站或图片网站")
    print("=" * 50)
    
    url = input("请输入要爬取的网页URL: ").strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    folder_name = input("请输入保存图片的文件夹名（直接回车将保存到桌面）: ").strip()
    
    # 获取桌面路径
    desktop_path = get_desktop_path()
    
    if not folder_name:
        # 如果用户没有输入文件夹名，直接使用桌面
        folder = desktop_path
    else:
        # 确保文件夹名称合法
        folder_name = "".join(x for x in folder_name if x.isalnum() or x in (' ', '-', '_'))
        if not folder_name:
            folder = desktop_path
        else:
            # 在桌面创建文件夹
            folder = os.path.join(desktop_path, folder_name)
    
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    print(f"\n开始获取图片链接...")
    image_urls = get_image_urls(url)
    
    if not image_urls:
        print("未找到任何图片，请检查URL是否正确或尝试其他网站")
        return
        
    print(f"共找到 {len(image_urls)} 张图片，开始下载...")
    success = 0
    
    with tqdm(total=len(image_urls), desc="下载进度") as pbar:
        for idx, img_url in enumerate(image_urls, 1):
            if download_image(img_url, folder, idx):
                success += 1
            pbar.update(1)
            
    print("\n下载完成！")
    print(f"成功下载: {success} 张图片")
    print(f"保存位置: {os.path.abspath(folder)}")
    print("\n提示：如果下载数量较少，可能是因为：")
    print("1. 网站有反爬虫机制")
    print("2. 图片链接需要特殊处理")
    print("3. 网站需要登录才能访问图片")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序出错: {str(e)}")
    finally:
        input("\n按回车键退出...") 