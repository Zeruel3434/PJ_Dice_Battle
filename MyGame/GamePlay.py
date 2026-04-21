import random
from collections import Counter

N = 6
D6 = 4

class GameState:
    def __init__(self):
        self.player_hp = 30 # เลือดผู้เล่น
        self.ai_hp = 30 # เลือด AI
        self.turn = "player" # ถึงตาผู้เล่นก่อน
        self.reroll_left = 2 #reroll ต่อเทิร์น
        self.player_dice = [0] * N  # ลูกเต๋าทั้งหมด (N ลูก) ของผู้เล่น
        self.ai_dice = [0] * N  #และ AI
        self.picked = [False] * N
        self.reroll_sel = [False] * N
        self.game_over = False # สถานะเกม 
        self.winner = None
        self.ai_attack_bonus = 1   # โบนัสโจมตีของ AI
        self.new_turn()  #เริ่มเกมทันที

    def roll_dice(self): #ทอยเต๋า
        return [random.randint(1, 6) for _ in range(D6)] + [random.randint(1, 4) for _ in range(N - D6)]

    def ai_best(self, dice, take):  #ai หาค่ามากสุดใช้ป้องกันกับโจมตี
        return sum(sorted(dice, reverse=True)[:take])

    def new_turn(self): #รีค่าเมื่อเริ่มเทิร์นใหม่
        self.player_dice = self.roll_dice()
        self.ai_dice = self.roll_dice()
        self.reroll_left = 2
        self.picked = [False] * N
        self.reroll_sel = [False] * N

    def reroll(self): #reroll เฉพาะตำแหน่งที่เลือก
        if self.reroll_left <= 0 or self.game_over:
            return
        if not any(self.reroll_sel):
            return
        for i in range(N):
            if not self.reroll_sel[i]:
                continue
            self.player_dice[i] = random.randint(1, 6) if i < D6 else random.randint(1, 4)
        self.reroll_left -= 1
        self.reroll_sel = [False] * N

    def get_selected_sum(self):# รวมค่าลูกเต๋าที่ถูกเลือกเอาไว้ใช้คำนวณโจมตีหรือป้องกัน
        return sum(d for d, p in zip(self.player_dice, self.picked) if p)

    def _has_triplet(self):   # ตรวจสอบว่าในลูกเต๋าที่เลือก มีเลขเดียวกันตั้งแต่ 3 ลูกขึ้นไปหรือไม่
       
        selected_dice = [d for d, p in zip(self.player_dice, self.picked) if p]
        ctr = Counter(selected_dice)
        return any(v >= 3 for v in ctr.values())

    def handle_confirm(self): # จัดการเมื่อ กด "ยืนยัน" หลังเลือกลูกเต๋า
        if self.turn == "player":
            base_dmg = self.get_selected_sum()
            guard = self.ai_best(self.ai_dice, 2)
            dmg = max(0, base_dmg - guard)           
            if dmg > 0 and self._has_triplet():
                 dmg += dmg   
            self.ai_hp -= dmg
            self.game_over = self.ai_hp <= 0
            self.winner = "player" if self.game_over else None
            if not self.game_over:
                self.turn = "ai"
                self.new_turn()
        else: # AI โจมตี เลือกลูกที่ดีที่สุด 3 ลูก
            ai_picked = [False] * N            
            best_dice_indices = sorted(range(N), key=lambda i: self.ai_dice[i], reverse=True)[:3]
            for i in best_dice_indices:
                ai_picked[i] = True
            base_dmg = self.ai_best(self.ai_dice, 3)
            guard = self.get_selected_sum()
            dmg = max(0, base_dmg - guard) +self.ai_attack_bonus     
            self.player_hp -= dmg
            self.game_over = self.player_hp <= 0
            self.winner = "ai" if self.game_over else None
            if not self.game_over:
                self.ai_attack_bonus += 1 
                self.turn = "player"
                self.new_turn()

    def reset(self): #ริ่มเกมใหม่ รีเซ็ตทุกอย่าง
        self.player_hp = 30
        self.ai_hp = 30
        self.turn = "player"
        self.game_over = False
        self.winner = None
        self.damage_last = 0
        self.damage_last_to = None
        self.ai_attack_bonus = 1
        self.new_turn()
