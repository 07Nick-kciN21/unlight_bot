# =============================================================================
# Unlight Bot 調試輔助工具
# =============================================================================

import cv2
import numpy as np
import pyautogui
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

class CoordinateHelper:
    """座標調整輔助工具"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Unlight Bot 座標調整工具")
        self.root.geometry("500x400")
        
        self.current_pos = (0, 0)
        self.setup_ui()
        
    def setup_ui(self):
        # 當前座標顯示
        self.pos_label = tk.Label(self.root, text="當前座標: (0, 0)", font=("Arial", 12))
        self.pos_label.pack(pady=10)
        
        # 更新座標按鈕
        tk.Button(self.root, text="獲取滑鼠座標", command=self.update_position).pack(pady=5)
        
        # 手牌區域設定
        frame1 = tk.Frame(self.root)
        frame1.pack(pady=10)
        
        tk.Label(frame1, text="手牌區域設定:").pack()
        
        # 座標輸入框
        coord_frame = tk.Frame(frame1)
        coord_frame.pack()
        
        tk.Label(coord_frame, text="X:").grid(row=0, column=0)
        self.x_entry = tk.Entry(coord_frame, width=8)
        self.x_entry.grid(row=0, column=1)
        self.x_entry.insert(0, "100")
        
        tk.Label(coord_frame, text="Y:").grid(row=0, column=2)
        self.y_entry = tk.Entry(coord_frame, width=8)
        self.y_entry.grid(row=0, column=3)
        self.y_entry.insert(0, "600")
        
        tk.Label(coord_frame, text="寬:").grid(row=1, column=0)
        self.w_entry = tk.Entry(coord_frame, width=8)
        self.w_entry.grid(row=1, column=1)
        self.w_entry.insert(0, "800")
        
        tk.Label(coord_frame, text="高:").grid(row=1, column=2)
        self.h_entry = tk.Entry(coord_frame, width=8)
        self.h_entry.grid(row=1, column=3)
        self.h_entry.insert(0, "150")
        
        # 測試按鈕
        tk.Button(frame1, text="測試手牌區域", command=self.test_hand_area).pack(pady=5)
        tk.Button(frame1, text="保存設定", command=self.save_settings).pack(pady=5)
        
        # 卡牌尺寸設定
        frame2 = tk.Frame(self.root)
        frame2.pack(pady=10)
        
        tk.Label(frame2, text="卡牌尺寸設定:").pack()
        
        size_frame = tk.Frame(frame2)
        size_frame.pack()
        
        tk.Label(size_frame, text="卡牌寬:").grid(row=0, column=0)
        self.card_w_entry = tk.Entry(size_frame, width=8)
        self.card_w_entry.grid(row=0, column=1)
        self.card_w_entry.insert(0, "80")
        
        tk.Label(size_frame, text="卡牌高:").grid(row=0, column=2)
        self.card_h_entry = tk.Entry(size_frame, width=8)
        self.card_h_entry.grid(row=0, column=3)
        self.card_h_entry.insert(0, "120")
        
        tk.Label(size_frame, text="間距:").grid(row=1, column=0)
        self.spacing_entry = tk.Entry(size_frame, width=8)
        self.spacing_entry.grid(row=1, column=1)
        self.spacing_entry.insert(0, "90")
        
        # 自動更新座標
        self.auto_update()
        
    def auto_update(self):
        """自動更新滑鼠座標"""
        pos = pyautogui.position()
        self.pos_label.config(text=f"當前座標: ({pos.x}, {pos.y})")
        self.root.after(100, self.auto_update)
    
    def update_position(self):
        """手動更新座標到輸入框"""
        pos = pyautogui.position()
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, str(pos.x))
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, str(pos.y))
    
    def test_hand_area(self):
        """測試手牌區域"""
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            w = int(self.w_entry.get())
            h = int(self.h_entry.get())
            
            # 截取區域
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # 保存測試圖片
            cv2.imwrite("test_hand_region.png", screenshot_cv)
            messagebox.showinfo("成功", "手牌區域已保存為 test_hand_region.png")
            
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的數字")
    
    def save_settings(self):
        """保存設定到檔案"""
        try:
            settings = {
                "hand_area": {
                    "x": int(self.x_entry.get()),
                    "y": int(self.y_entry.get()),
                    "width": int(self.w_entry.get()),
                    "height": int(self.h_entry.get())
                },
                "card_settings": {
                    "width": int(self.card_w_entry.get()),
                    "height": int(self.card_h_entry.get()),
                    "spacing": int(self.spacing_entry.get())
                }
            }
            
            with open("bot_settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("成功", "設定已保存到 bot_settings.json")
            
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的數字")
    
    def run(self):
        """運行工具"""
        self.root.mainloop()

class TemplateCreator:
    """模板圖片創建工具"""
    
    def __init__(self):
        self.templates_dir = Path("templates")
        self.templates_dir.mkdir(exist_ok=True)
        
    def create_template_from_screenshot(self, symbol_name: str, region: tuple):
        """從截圖創建模板"""
        x, y, w, h = region
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # 轉換為灰度
        gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
        
        # 保存模板
        template_path = self.templates_dir / f"{symbol_name}_template.png"
        cv2.imwrite(str(template_path), gray)
        
        print(f"模板已保存: {template_path}")
        return template_path
    
    def interactive_template_creation(self):
        """交互式模板創建"""
        symbols = ["move", "shield", "sword", "gun", "special"]
        
        print("=== 模板創建工具 ===")
        print("將滑鼠移動到要擷取的符號位置，然後按Enter")
        
        for symbol in symbols:
            input(f"準備擷取 {symbol} 符號，按Enter繼續...")
            
            # 獲取當前滑鼠位置
            pos = pyautogui.position()
            
            # 擷取小區域 (30x30 像素)
            region = (pos.x - 15, pos.y - 15, 30, 30)
            
            try:
                template_path = self.create_template_from_screenshot(symbol, region)
                print(f"✅ {symbol} 模板創建完成")
            except Exception as e:
                print(f"❌ {symbol} 模板創建失敗: {e}")

class LogAnalyzer:
    """日誌分析工具"""
    
    def __init__(self):
        self.logs = []
    
    def analyze_scan_results(self, json_file: str = "scanned_cards.json"):
        """分析掃描結果"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                cards_data = json.load(f)
            
            print(f"=== 掃描結果分析 ({json_file}) ===")
            print(f"找到卡牌數量: {len(cards_data)}")
            
            # 統計符號分布
            symbol_count = {}
            for card in cards_data:
                top_symbol = card['top_symbol']
                bottom_symbol = card['bottom_symbol']
                
                symbol_count[top_symbol] = symbol_count.get(top_symbol, 0) + 1
                symbol_count[bottom_symbol] = symbol_count.get(bottom_symbol, 0) + 1
            
            print("\n符號統計:")
            for symbol, count in symbol_count.items():
                print(f"  {symbol}: {count} 次")
            
            # 數值分析
            values = []
            for card in cards_data:
                values.extend([card['top_value'], card['bottom_value']])
            
            if values:
                print(f"\n數值統計:")
                print(f"  平均值: {sum(values) / len(values):.2f}")
                print(f"  最大值: {max(values)}")
                print(f"  最小值: {min(values)}")
            
            return cards_data
            
        except FileNotFoundError:
            print(f"找不到檔案: {json_file}")
            return None
        except Exception as e:
            print(f"分析出錯: {e}")
            return None

class PerformanceMonitor:
    """性能監控工具"""
    
    def __init__(self):
        self.timing_data = {}
        self.start_times = {}
    
    def start_timer(self, operation: str):
        """開始計時"""
        import time
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str):
        """結束計時"""
        import time
        if operation in self.start_times:
            elapsed = time.time() - self.start_times[operation]
            
            if operation not in self.timing_data:
                self.timing_data[operation] = []
            
            self.timing_data[operation].append(elapsed)
            print(f"{operation}: {elapsed:.3f}秒")
            
            del self.start_times[operation]
            return elapsed
        return None
    
    def get_performance_report(self):
        """獲取性能報告"""
        print("\n=== 性能報告 ===")
        for operation, times in self.timing_data.items():
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"{operation}:")
            print(f"  平均: {avg_time:.3f}秒")
            print(f"  最快: {min_time:.3f}秒") 
            print(f"  最慢: {max_time:.3f}秒")
            print(f"  執行次數: {len(times)}")

def run_debug_tools():
    """運行調試工具選單"""
    print("=== Unlight Bot 調試工具 ===")
    print("1. 座標調整工具")
    print("2. 模板創建工具")
    print("3. 日誌分析工具")
    print("4. 性能監控測試")
    print("0. 返回主選單")
    
    choice = input("請選擇工具 (0-4): ").strip()
    
    if choice == '1':
        print("啟動座標調整工具...")
        helper = CoordinateHelper()
        helper.run()
        
    elif choice == '2':
        print("啟動模板創建工具...")
        creator = TemplateCreator()
        creator.interactive_template_creation()
        
    elif choice == '3':
        print("啟動日誌分析工具...")
        analyzer = LogAnalyzer()
        analyzer.analyze_scan_results()
        
    elif choice == '4':
        print("性能監控測試...")
        monitor = PerformanceMonitor()
        
        # 示例性能測試
        monitor.start_timer("截圖測試")
        pyautogui.screenshot()
        monitor.end_timer("截圖測試")
        
        monitor.get_performance_report()
        
    elif choice == '0':
        return
    else:
        print("無效選擇")

if __name__ == "__main__":
    run_debug_tools()