import os
import zipfile
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

KAGGLE_DATASET = "olistbr/brazilian-ecommerce"
DOWNLOAD_DIR = "data/raw/olist"

def download_and_extract():
    # Đảm bảo thư mục tồn tại
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    logger.info(f"Đang tải dataset {KAGGLE_DATASET} từ Kaggle...")
    try:
        # Chạy lệnh kaggle cli để tải
        subprocess.run(["kaggle", "datasets", "download", "-d", KAGGLE_DATASET, "-p", DOWNLOAD_DIR], check=True)
        
        zip_path = os.path.join(DOWNLOAD_DIR, "brazilian-ecommerce.zip")
        if os.path.exists(zip_path):
            logger.info("Đang giải nén file...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(DOWNLOAD_DIR)
            
            # Xóa file zip sau khi giải nén xong cho nhẹ máy
            os.remove(zip_path)
            logger.info(f"Giải nén thành công! Toàn bộ file đã nằm trong: {DOWNLOAD_DIR}")
        else:
            logger.error("Lỗi: Không tìm thấy file zip sau khi tải.")
            
    except subprocess.CalledProcessError as e:
        logger.error("Lỗi khi tải từ Kaggle. Bạn đã cấu hình file ~/.kaggle/kaggle.json chưa?")
        logger.error(f"Chi tiết: {e}")
    except FileNotFoundError:
        logger.error("Không tìm thấy lệnh kaggle. Hãy chạy 'pip install kaggle'")

if __name__ == "__main__":
    download_and_extract()
