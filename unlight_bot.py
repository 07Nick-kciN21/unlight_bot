import cv2
import numpy as np
import pyautogui
import time
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from enum import Enum

class CardSymbol(Enum):
    MOVE = "移動"
    SHIELD = "盾牌"
    SWORD = "劍"
    GUN = "槍"
    SPECIAL = "特殊"

class GamePhase(Enum):
    DEAL = "發牌"
    MOVE = "移動"
    ATTACK = "攻擊"
    DEFEND = "防守"

@dataclass
class Card:
    """卡牌資訊 - 類似撲克牌結構"""
    position: Tuple[int, int]  # 卡牌在畫面上的位置
    center_position: Tuple[int, int]  # 中央切換區域位置
    top_symbol: CardSymbol
    top_value: int
    bottom_symbol: CardSymbol
    bottom_value: int
    current_side: str = "top"  # "top" 或 "bottom"
    
    def get_current_symbol(self) -> CardSymbol:
        return self.top_symbol if self.current_side == "top" else self.bottom_symbol
    
    def get_current_value(self) -> int:
        return self.top_value if self.current_side == "top" else self.bottom_value

class UnlightBot:
    def __init__(self):
        self.cards: List[Card] = []
        self.current_phase = GamePhase.DEAL
        self.screen_width, self.screen_height = pyautogui.size()
        self.phase_requirements = {}  # 階段需求配置
        
        # 設定安全機制
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # 預設的卡牌區域（需要根據實際遊戲調整）
        self.hand_area = (100, 600, 800, 150)  # (x, y, width, height)
        
        # 載入階段需求配置
        self.load_phase_requirements()
    
    def capture_screen(self) -> np.ndarray:
        """截取螢幕畫面"""
        screenshot = pyautogui.screenshot()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    def detect_game_phase(self, image: np.ndarray) -> GamePhase:
        """檢測當前遊戲階段"""
        # 這裡需要根據遊戲UI的特徵來判斷階段
        # 例如：檢測特定的階段指示器顏色或文字
        
        # 示例：檢測階段指示器（需要根據實際遊戲調整）
        phase_areas = {
            GamePhase.DEAL: (50, 50, 100, 30),
            GamePhase.MOVE: (150, 50, 100, 30),
            GamePhase.ATTACK: (250, 50, 100, 30),
            GamePhase.DEFEND: (350, 50, 100, 30)
        }
        
        # 簡化示例，實際需要圖像識別
        return GamePhase.MOVE  # 預設返回移動階段
    
    def detect_card_symbol(self, card_image: np.ndarray) -> Tuple[CardSymbol, int]:
        """識別卡牌符號和數值"""
        # 這裡需要實現圖像識別邏輯
        # 可以使用模板匹配或者訓練的機器學習模型
        
        # 示例：使用模板匹配識別符號
        symbols = {
            CardSymbol.MOVE: "move_template.png",
            CardSymbol.SHIELD: "shield_template.png",
            CardSymbol.SWORD: "sword_template.png",
            CardSymbol.GUN: "gun_template.png",
            CardSymbol.SPECIAL: "special_template.png"
        }
        
        best_match = CardSymbol.MOVE
        best_score = 0
        
        for symbol, template_path in symbols.items():
            try:
                # 載入模板（需要預先準備符號的模板圖片）
                template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                if template is not None:
                    card_gray = cv2.cvtColor(card_image, cv2.COLOR_BGR2GRAY)
                    result = cv2.matchTemplate(card_gray, template, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, _ = cv2.minMaxLoc(result)
                    
                    if max_val > best_score:
                        best_score = max_val
                        best_match = symbol
            except:
                continue
        
        # 識別數值（需要OCR或者數字模板匹配）
        value = self.extract_card_value(card_image)
        
        return best_match, value
    
    def extract_card_value(self, card_image: np.ndarray) -> int:
        """提取卡牌數值"""
        # 這裡可以使用OCR或者數字模板匹配
        # 示例：使用pytesseract進行OCR
        try:
            import pytesseract
            gray = cv2.cvtColor(card_image, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray, config='--psm 8 -c tessedit_char_whitelist=0123456789')
            return int(text.strip()) if text.strip().isdigit() else 1
        except:
            return 1  # 預設值
    
    def scan_hand_cards(self) -> List[Card]:
        """掃描手牌"""
        image = self.capture_screen()
        cards = []
        
        # 在手牌區域尋找卡牌
        x, y, w, h = self.hand_area
        hand_region = image[y:y+h, x:x+w]
        
        # 假設卡牌按固定間距排列
        card_width = 80
        card_height = 120
        card_spacing = 90
        
        for i in range(6):  # 假設最多6張手牌
            card_x = x + i * card_spacing
            card_y = y + 10
            
            if card_x + card_width > x + w:
                break
            
            card_image = image[card_y:card_y+card_height, card_x:card_x+card_width]
            
            # 檢查是否有卡牌（可以通過檢測卡牌邊框或特徵）
            if self.has_card_at_position(card_image):
                # 識別卡牌上下兩面（類似撲克牌結構）
                # 上半部分是正面，下半部分是反面（上下顛倒）
                card_height_quarter = card_height // 4
                top_region = card_image[card_height_quarter:card_height//2, :]
                bottom_region = card_image[card_height//2:card_height-card_height_quarter, :]
                
                # 下半部分需要旋轉180度來識別
                bottom_region_rotated = cv2.rotate(bottom_region, cv2.ROTATE_180)
                
                top_symbol, top_value = self.detect_card_symbol(top_region)
                bottom_symbol, bottom_value = self.detect_card_symbol(bottom_region_rotated)
                
                # 計算中央切換區域（卡牌中央小區域）
                center_x = card_x + card_width // 2
                center_y = card_y + card_height // 2
                
                card = Card(
                    position=(card_x + card_width//2, card_y + card_height//2),
                    center_position=(center_x, center_y),
                    top_symbol=top_symbol,
                    top_value=top_value,
                    bottom_symbol=bottom_symbol,
                    bottom_value=bottom_value
                )
                cards.append(card)
        
        return cards
    
    def has_card_at_position(self, card_image: np.ndarray) -> bool:
        """檢查指定位置是否有卡牌"""
        # 簡單的邊緣檢測來判斷是否有卡牌
        gray = cv2.cvtColor(card_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        return np.sum(edges) > 1000  # 閾值需要調整
    
    def flip_card(self, card: Card):
        """翻轉卡牌（點擊卡牌中央區域）"""
        pyautogui.click(card.center_position[0], card.center_position[1])
        time.sleep(0.3)
        card.current_side = "bottom" if card.current_side == "top" else "top"
        print(f"翻轉卡牌到 {card.current_side} 面")
    
    def play_card(self, card: Card):
        """打出卡牌（點擊卡牌非中央區域）"""
        # 點擊卡牌邊緣區域來出牌，避免中央切換區域
        offset_x = 25  # 偏移到卡牌邊緣
        play_x = card.position[0] + offset_x
        play_y = card.position[1]
        
        pyautogui.click(play_x, play_y)
        time.sleep(0.3)
        print(f"打出卡牌: {card.get_current_symbol().value} {card.get_current_value()}")
    
    def find_optimal_combination(self, target_symbol: CardSymbol, 
                               target_value: int, 
                               phase: GamePhase) -> List[Card]:
        """尋找最佳卡牌組合"""
        available_cards = []
        
        # 根據階段篩選可用卡牌
        for card in self.cards:
            current_symbol = card.get_current_symbol()
            if self.symbol_matches_phase(current_symbol, phase):
                available_cards.append(card)
        
        # 也檢查翻面後的選項
        for card in self.cards:
            if card not in available_cards:
                # 檢查翻面後是否符合條件
                other_symbol = card.bottom_symbol if card.current_side == "top" else card.top_symbol
                if self.symbol_matches_phase(other_symbol, phase):
                    available_cards.append(card)
        
        # 動態規劃或貪心算法找最佳組合
        return self.dp_card_combination(available_cards, target_symbol, target_value)
    
    def dp_card_combination(self, cards: List[Card], 
                          target_symbol: CardSymbol, 
                          target_value: int) -> List[Card]:
        """使用動態規劃找最佳卡牌組合"""
        # 簡化版本：貪心算法
        suitable_cards = []
        
        for card in cards:
            current_symbol = card.get_current_symbol()
            if current_symbol != target_symbol:
                # 需要翻面
                other_symbol = card.bottom_symbol if card.current_side == "top" else card.top_symbol
                if other_symbol == target_symbol:
                    suitable_cards.append((card, True))  # (卡牌, 需要翻面)
            else:
                suitable_cards.append((card, False))
        
        # 按數值排序，優先選擇高數值卡牌
        suitable_cards.sort(key=lambda x: x[0].get_current_value() if not x[1] else 
                          (x[0].bottom_value if x[0].current_side == "top" else x[0].top_value),
                          reverse=True)
        
        selected_cards = []
        current_sum = 0
        
        for card, need_flip in suitable_cards:
            if need_flip:
                value = card.bottom_value if card.current_side == "top" else card.top_value
            else:
                value = card.get_current_value()
            
            if current_sum + value <= target_value:
                selected_cards.append(card)
                current_sum += value
                
                if current_sum == target_value:
                    break
        
        return selected_cards
    
    def symbol_matches_phase(self, symbol: CardSymbol, phase: GamePhase) -> bool:
        """檢查符號是否符合階段需求"""
        if phase == GamePhase.MOVE:
            return symbol == CardSymbol.MOVE
        elif phase == GamePhase.ATTACK:
            return symbol in [CardSymbol.SWORD, CardSymbol.GUN, CardSymbol.SPECIAL]
        elif phase == GamePhase.DEFEND:
            return symbol in [CardSymbol.SHIELD, CardSymbol.SPECIAL]
        return False
    
    def load_phase_requirements(self):
        """從txt文件載入階段需求"""
        try:
            with open('phase_requirements.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            current_phase = None
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.endswith('：') or line.endswith(':'):
                    # 階段標題
                    phase_name = line.rstrip('：:')
                    if phase_name == "移動":
                        current_phase = GamePhase.MOVE
                    elif phase_name == "攻擊":
                        current_phase = GamePhase.ATTACK
                    elif phase_name == "防守":
                        current_phase = GamePhase.DEFEND
                    
                    if current_phase:
                        self.phase_requirements[current_phase] = []
                
                elif current_phase and ('移' in line or '劍' in line or '槍' in line or '盾' in line or '特' in line):
                    # 解析需求，例如：移1 劍3
                    requirements = self.parse_requirements(line)
                    self.phase_requirements[current_phase].extend(requirements)
                    
        except FileNotFoundError:
            print("找不到 phase_requirements.txt 文件，將使用預設設定")
            self.create_default_requirements_file()
        except Exception as e:
            print(f"載入階段需求時出錯: {e}")
            self.create_default_requirements_file()
    
    def parse_requirements(self, line: str) -> List[Tuple[CardSymbol, int]]:
        """解析需求字符串"""
        requirements = []
        parts = line.split()
        
        for part in parts:
            if not part:
                continue
                
            symbol = None
            value = 0
            
            if part.startswith('移'):
                symbol = CardSymbol.MOVE
                value = int(part[1:]) if len(part) > 1 and part[1:].isdigit() else 1
            elif part.startswith('劍'):
                symbol = CardSymbol.SWORD
                value = int(part[1:]) if len(part) > 1 and part[1:].isdigit() else 1
            elif part.startswith('槍'):
                symbol = CardSymbol.GUN
                value = int(part[1:]) if len(part) > 1 and part[1:].isdigit() else 1
            elif part.startswith('盾'):
                symbol = CardSymbol.SHIELD
                value = int(part[1:]) if len(part) > 1 and part[1:].isdigit() else 1
            elif part.startswith('特'):
                symbol = CardSymbol.SPECIAL
                value = int(part[1:]) if len(part) > 1 and part[1:].isdigit() else 1
            
            if symbol:
                requirements.append((symbol, value))
        
        return requirements
    
    def create_default_requirements_file(self):
        """創建預設的需求配置文件"""
        default_content = """# Unlight 階段需求配置
# 格式：階段名稱：
#       符號+數值 符號+數值
# 符號：移(移動) 劍(劍) 槍(槍) 盾(盾牌) 特(特殊)

移動：
移1

攻擊：
劍3 特3

防守：
盾4
"""
        
        with open('phase_requirements.txt', 'w', encoding='utf-8') as f:
            f.write(default_content)
        
        print("已創建預設的 phase_requirements.txt 文件")
        self.load_phase_requirements()
    
    def execute_phase_requirements(self, phase: GamePhase):
        """執行階段需求"""
        if phase not in self.phase_requirements:
            print(f"沒有找到階段 {phase.value} 的需求配置")
            return
        
        requirements = self.phase_requirements[phase]
        print(f"執行階段 {phase.value} 需求: {requirements}")
        
        for symbol, target_value in requirements:
            optimal_cards = self.find_optimal_combination(symbol, target_value, phase)
            
            if not optimal_cards:
                print(f"沒有找到符合 {symbol.value} {target_value} 的卡牌組合")
                continue
            
            total_value = 0
            print(f"找到 {len(optimal_cards)} 張卡牌組合:")
            
            # 翻轉需要翻面的卡牌
            for card in optimal_cards:
                current_symbol = card.get_current_symbol()
                if current_symbol != symbol:
                    print(f"  翻轉卡牌 {card.position} 從 {current_symbol.value} 到 {symbol.value}")
                    self.flip_card(card)
                    time.sleep(0.2)
            
            # 打出卡牌
            for card in optimal_cards:
                current_value = card.get_current_value()
                total_value += current_value
                print(f"  打出: {card.get_current_symbol().value} {current_value}")
                self.play_card(card)
                time.sleep(0.5)
            
            print(f"完成需求: {symbol.value} 總計 {total_value}/{target_value}")
            time.sleep(1)
    
    def execute_turn(self, target_symbol: CardSymbol = None, target_value: int = None):
        """執行一回合"""
        # 1. 掃描手牌
        self.cards = self.scan_hand_cards()
        print(f"掃描到 {len(self.cards)} 張手牌")
        
        # 2. 檢測當前階段
        image = self.capture_screen()
        self.current_phase = self.detect_game_phase(image)
        print(f"當前階段: {self.current_phase.value}")
        
        # 3. 如果沒有指定目標，使用配置文件的需求
        if target_symbol is None or target_value is None:
            self.execute_phase_requirements(self.current_phase)
            return
        
        # 4. 使用指定的目標
        optimal_cards = self.find_optimal_combination(target_symbol, target_value, self.current_phase)
        
        if not optimal_cards:
            print("沒有找到合適的卡牌組合")
            return
        
        print(f"找到 {len(optimal_cards)} 張卡牌組合")
        
        # 5. 翻轉需要翻面的卡牌
        for card in optimal_cards:
            current_symbol = card.get_current_symbol()
            if current_symbol != target_symbol:
                print(f"翻轉卡牌 {card.position}")
                self.flip_card(card)
        
        # 6. 打出卡牌
        for card in optimal_cards:
            print(f"打出卡牌 {card.position}")
            self.play_card(card)
            time.sleep(0.5)
    
    def run_auto_play(self):
        """自動遊戲主循環"""
        print("開始自動遊戲...")
        print("階段需求配置:")
        for phase, requirements in self.phase_requirements.items():
            print(f"  {phase.value}: {[(r[0].value, r[1]) for r in requirements]}")
        
        while True:
            try:
                # 根據配置文件執行每個階段
                self.execute_turn()
                time.sleep(2)
                
            except KeyboardInterrupt:
                print("停止自動遊戲")
                break
            except Exception as e:
                print(f"錯誤: {e}")
                time.sleep(1)

# 使用示例
if __name__ == "__main__":
    bot = UnlightBot()
    
    # 手動執行單次操作（使用配置文件）
    # bot.execute_turn()
    
    # 手動執行單次操作（指定目標）
    # bot.execute_turn(CardSymbol.MOVE, 3)
    
    # 開始自動遊戲（使用配置文件）
    # bot.run_auto_play()
    
    # 測試掃描手牌
    cards = bot.scan_hand_cards()
    for i, card in enumerate(cards):
        print(f"卡牌 {i+1}: 位置{card.position}, 中央{card.center_position}")
        print(f"  正面: {card.top_symbol.value}({card.top_value})")
        print(f"  背面: {card.bottom_symbol.value}({card.bottom_value})")
        print(f"  當前: {card.get_current_symbol().value}({card.get_current_value()})")
    
    # 顯示當前配置
    print("\n當前階段需求配置:")
    for phase, requirements in bot.phase_requirements.items():
        print(f"{phase.value}: {[(r[0].value, r[1]) for r in requirements]}")