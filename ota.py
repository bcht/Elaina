import os
import sys
import zipfile
import shutil
import logging
import requests
import subprocess
from io import BytesIO

logger = logging.getLogger(__name__)

"""澄清一下，这玩意不全是我写的
稍微用了一下ai，改了一下，对不住qwq"""

def get_latest_release(repo):
    """从 GitHub API 获取最新 Release 信息"""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            logger.error(f"获取 Release 失败: HTTP {response.status_code}")
            return None
        
        data = response.json()
        return {
            "version": data["name"],
            "zip_url": data["zipball_url"],
            "name": data["tag_name"]
        }
    except Exception as e:
        logger.error(f"获取 Release 出错: {e}")
        return None

def download_and_extract(zip_url):
    """下载 zip 并解压到临时目录"""
    try:
        logger.info("正在下载更新包...")
        response = requests.get(zip_url, timeout=60)
        
        if response.status_code != 200:
            logger.error(f"下载失败: HTTP {response.status_code}")
            return None
        
        temp_dir = "_ota_temp"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            root_folder = z.namelist()[0].split('/')[0]
            z.extractall(temp_dir)
        
        return os.path.join(temp_dir, root_folder)
        
    except Exception as e:
        logger.error(f"下载解压出错: {e}")
        return None

def install_dependencies(source_dir):
    """安装依赖"""
    req_file = os.path.join(source_dir, "requirements.txt")
    
    if not os.path.exists(req_file):
        logger.info("没有 requirements.txt，跳过依赖安装")
        return True
    
    try:
        logger.info("正在安装依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        logger.info("依赖安装完成")
        return True
    except Exception as e:
        logger.error(f"安装依赖失败: {e}")
        return False

def replace_files(source_dir, keep_files=None):
    """替换所有文件（跳过 config.py），并删除废弃文件"""
    try:
        logger.info("正在替换文件...")
        
        # 默认保留的文件
        if keep_files is None:
            keep_files = ["config.py","elaina.db"]
        else:
            keep_files = list(set(keep_files + ["config.py","elaina.db"]))  # config.py elaina.db 永远保留
        
        # 获取源文件列表（排除要保留的）
        source_items = {item for item in os.listdir(source_dir) if item not in keep_files}
        
        # 删除目标目录中的废弃文件
        for item in os.listdir("."):
            if item in keep_files or item.startswith("_ota_temp"):
                continue
            if item not in source_items:
                target = item
                logger.info(f"删除废弃文件: {item}")
                if os.path.isdir(target):
                    shutil.rmtree(target)
                else:
                    os.remove(target)
        
        # 复制新文件
        for item in source_items:
            src = os.path.join(source_dir, item)
            dst = item
            
            if os.path.exists(dst):
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                else:
                    os.remove(dst)
            
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        
        logger.info("文件替换完成")
        return True
        
    except Exception as e:
        logger.error(f"文件替换出错: {e}")
        return False

def cleanup():
    """清理临时文件"""
    temp_dir = "_ota_temp"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        logger.info("临时文件已清理")

def restart_program():
    """重启程序"""
    logger.info("正在重启...")
    python = sys.executable
    os.execl(python, python, *sys.argv)

def check_and_update(current_version, repo, keep_file):
    """主函数：检查并执行更新"""
    
    # 1. 获取最新 Release
    logger.info("正在检查更新...")
    release = get_latest_release(repo)
    
    if not release:
        return False, "检查更新失败"
    
    latest_version = release["version"]
    logger.info(f"当前版本: {current_version}, 最新版本: {latest_version}")
    
    # 2. 比较版本
    if latest_version == current_version:
        logger.info("已是最新版本")
        return False, "已是最新版本"
    
    # 3. 下载并解压
    source_dir = download_and_extract(release["zip_url"])
    if not source_dir:
        cleanup()
        return False, "下载失败"
    
    # 4. 安装依赖
    if not install_dependencies(source_dir):
        cleanup()
        return False, "依赖安装失败"
    
    # 5. 替换文件
    if not replace_files(source_dir,keep_files=keep_file):
        cleanup()
        return False, "文件替换失败"
    
    # 6. 清理临时文件
    cleanup()
    
    logger.info(f"更新完成！新版本: {latest_version}")
    return True, f"已更新到 {latest_version}"

def ota_update(current_version, repo, keep_file=None, auto_restart=True):
    """OTA 更新入口"""
    success, msg = check_and_update(current_version, repo, keep_file)
    
    if success and auto_restart:
        logger.info("即将重启...")
        restart_program()
    
    return success, msg