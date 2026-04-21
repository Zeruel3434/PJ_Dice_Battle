
import os           # ใช้ในการจัดการ path ของไฟล์รูปภาพและฟอนต์
import sys          # สำหรับการออกจากโปรแกรมด้วย sys.exit
import pygame       # ใช้งาน Pygame สำหรับกราฟิกและ UI

from GamePlay import GameState, N, D6  # นำเข้าคลาสและค่าคงที่จากโมดูล GamePlay
from GameEffect import Effect # นำเข้าคลาส GameEffect

pygame.init()       # เริ่มการทำงานของ Pygame

# กำหนดค่าคงที่พื้นฐานของหน้าจอ
WIDTH, HEIGHT = 1500, 800        # ขนาดหน้าต่างเกม
FPS = 60                         # อัตราเฟรมต่อวินาที

# โหลดรูปภาพตัวละครสำหรับแสดงผล
Gil_AF = pygame.image.load(os.path.join("Gallery", "Gil_AF.png"))
Saber_AF = pygame.image.load(os.path.join("Gallery", "Saber_AF.png"))

def load_effect(path, size=(800, 800), start=1, end=10, ext="png"):
    """โหลด animation effect จาก path (เฟรม 1 ถึง end), ส่งคืนลิสต์ surface เช่น "1.png", "2.png", ..., จนครบจำนวนที่ตั้งไว้"""
    frames = []
    for i in range(start, end + 1): # วนลูปตั้งแต่ start ถึง end เพื่อเช็คไฟล์ภาพแต่ละเฟรม
        img_path = os.path.join(path, f"{i}.{ext}")
        if os.path.isfile(img_path): # ถ้าไฟล์นั้นมีอยู่จริง จะโหลดเข้ามา
            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.smoothscale(img, size)
            frames.append(img)
        else:
            print(f"ไม่พบไฟล์ {img_path}")
    return frames

# ฟังก์ชันสำหรับโหลดฟอนต์ภาษาไทย
def load_thai_font(size, bold=False):
    
    #ค้นหาและโหลดฟอนต์ Sarabun (หรือ Tahoma ถ้าไม่พบ)
    here = os.path.dirname(os.path.abspath(__file__))
    for rel in (
        "Sarabun-Medium.ttf",
        "Sarabun-Medium.otf",
        os.path.join("fonts", "Sarabun-Medium.ttf"),
        os.path.join("fonts", "Sarabun-Medium.otf"),
    ):
        path = os.path.join(here, rel)
        if os.path.isfile(path):
            f = pygame.font.Font(path, size)
            if bold:
                f.set_bold(True)
            return f
    return pygame.font.SysFont("Tahoma", size, bold=bold)

# สร้างหน้าต่างหลักของเกม
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dice Battle")
clock = pygame.time.Clock()   # ตัวจับเวลา เพื่อควบคุม FPS

# กำหนดฟอนต์ที่ใช้ในเกม
font = load_thai_font(36)
font_small = load_thai_font(24)
font_title = load_thai_font(48)

# สีต่าง ๆ ที่ใช้ในเกม (Color constants)
BG = (24, 26, 32)               # พื้นหลัง
PANEL = (40, 44, 54)            # แผง
TEXT = (235, 238, 245)          # ข้อความปกติ
MUTED = (140, 145, 160)         # ข้อความสีจาง
ACCENT = (88, 166, 255)         # สีเน้น/แอคเซนต์
PLAYER_ATK = (255, 120, 100)    # สีโจมตีผู้เล่น
PLAYER_DEF = (100, 200, 255)    # สีป้องกันผู้เล่น
AI_COLOR = (180, 100, 220)      # สีฝั่ง AI
BTN_REROLL = (70, 90, 150)      # ปุ่ม reroll
BTN_CONFIRM = (60, 140, 90)     # ปุ่ม confirm
CELL_ATK = (72, 44, 48)         # ลูกเต๋าโจมตี
CELL_DEF = (38, 52, 82)         # ลูกเต๋าป้องกัน

# ค่าคงที่สำหรับจัดวางแถวลูกเต๋า
DX = 500     # ตำแหน่งเริ่มของแถวลูกเต๋า
GAP = 80     # ระยะห่างระหว่างลูกเต๋าแต่ละลูก
SZ = 70      # ขนาดลูกเต๋าแต่ละลูก (สี่เหลี่ยม)
ROW_Y = 500  # ตำแหน่งแนวตั้งของแถวลูกเต๋าผู้เล่น

# ฟังก์ชันสำหรับเขียนข้อความบนจอ
def draw_text(surf, text, pos, color=TEXT, fnt=font, anchor="topleft"):
    """
    วาดข้อความ text ลงบน surf ที่ตำแหน่ง pos
    anchor: จุดอ้างอิงสำหรับข้อความ เช่น "center", "midtop", "topleft" ฯลฯ
    """
    img = fnt.render(text, True, color)
    rect = img.get_rect()
    setattr(rect, anchor, pos)   # ปรับจุด anchor
    surf.blit(img, rect)

# ฟังก์ชันวาดแถวลูกเต๋าผู้เล่น
def draw_dice_row_player(surf, dice, y, label, label_color, picked=None, reroll_sel=None, pick_atk=None):
    """
    วาดแถวลูกเต๋าบน surf ที่ตำแหน่ง y พร้อม label
    dice: ลิสต์ค่าลูกเต๋า (แสดงตัวเลข)
    label: ข้อความอธิบายแถว
    label_color: สีข้อความ label
    picked: เลือกลูกเต๋าตัวไหนบ้าง (สถานะ Highlight)
    reroll_sel: เลือกสำหรับ reroll หรือไม่
    pick_atk: แถวนี้กำลัง "เลือกโจมตี" อยู่หรือไม่ (เงื่อนไขสี)
    """
    draw_text(surf, label, (WIDTH // 2, y - 8), label_color, font_small, anchor="midbottom")
    for i in range(N): #วาดช่องลูกเต๋าแต่ละช่องเรียงในแนวนอน (วนลูปจาก i=0 ถึง N-1)
        x = 50 + i * GAP #ระยะห่างระหว่างเต๋า
        r = pygame.Rect(x, y, SZ, SZ)   #สร้างสี่เหลี่ยมแต่ละช่องที่ตำแหน่ง x, y     
        fill = PANEL if picked is None else (CELL_ATK if pick_atk and picked[i] else CELL_DEF if picked and picked[i] else PANEL) #กำหนดสีลูกเต๋า
        pygame.draw.rect(surf, fill, r, border_radius=8) #กำหนดมุม
        bd, w = (ACCENT, 3) if reroll_sel and reroll_sel[i] else (MUTED, 2) #สีกรอบมุม
        pygame.draw.rect(surf, bd, r, w, border_radius=8) #กำหนดมุมของขอบ
        cx = x + SZ // 2 #หาจุดกลางวาดเลข
        kind = "d6" if i < D6 else "d4" #d6 อยู่หน้า d4    
        draw_text(surf, str(dice[i]), (cx, y + SZ * 0.28), TEXT, font, anchor="center")#เขียนเลขลูกเต๋า
        draw_text(surf, kind, (cx, y + SZ * 0.78), MUTED, font_small, anchor="center") #เขียนชนิดลูกเต๋า

# ฟังก์ชันวาดแถวลูกเต๋า AI
def draw_dice_row_ai(surf, dice, y, label, label_color, picked=None, reroll_sel=None, pick_atk=None):
    draw_text(surf, label, (WIDTH // 2, y - 8), label_color, font_small, anchor="midbottom")
    for i in range(N):
        x = 1000 + i * GAP
        r = pygame.Rect(x, y, SZ, SZ)        
        fill = PANEL if picked is None else (CELL_ATK if pick_atk and picked[i] else CELL_DEF if picked and picked[i] else PANEL)
        pygame.draw.rect(surf, fill, r, border_radius=8)
        bd, w = (ACCENT, 3) if reroll_sel and reroll_sel[i] else (MUTED, 2)
        pygame.draw.rect(surf, bd, r, w, border_radius=8)
        cx = x + SZ // 2
        kind = "d6" if i < D6 else "d4"      # ระบุชนิดลูกเต๋า
        draw_text(surf, str(dice[i]), (cx, y + SZ * 0.28), TEXT, font, anchor="center")
        draw_text(surf, kind, (cx, y + SZ * 0.78), MUTED, font_small, anchor="center")
    

# ใช้สำหรับตรวจสอบการคลิกเมาส์ ตรงกับช่องลูกเต๋าช่องใหน
def dice_index_at(mx, my):
    for i in range(N):
        if pygame.Rect(50 + i * GAP, 250, SZ, SZ).collidepoint(mx, my):
            return i
    return None

# ฟังก์ชันสำหรับดาเมจ
class FloatingDamage:
    def __init__(self):
        self.damages = []  # แต่ละดาเมจ: dict มี key: 'text', 'color', 'pos', 'timer'

    def spawn(self, text, color, pos):
        self.damages.append({
            'text': text,
            'color': color,
            'pos': list(pos),   # [x, y]
            'timer': 60,       # แสดงผล 60 frame
        })

    def update(self):
        # ย้ายดาเมจขึ้น, ลด timer
        to_keep = []
        for d in self.damages:
            d['pos'][1] -= 1
            d['timer'] -= 1
            if d['timer'] > 0:
                to_keep.append(d)
        self.damages = to_keep

    def draw(self, surf, font):
        for d in self.damages:
            alpha = max(40, min(255, d['timer'] * 6))
            font_img = font.render(d['text'], True, d['color'])
            font_img.set_alpha(alpha)
            rect = font_img.get_rect(center=d['pos'])
            surf.blit(font_img, rect)

f_damage = FloatingDamage()

effect_frames = load_effect(
    os.path.join("Effect", "0101"),
    size=(700, 700),
    start=1,
    end=10,
    ext="png"
)


# สร้างอินสแตนซ์ของเอฟเฟกต์
player_atk_effect = Effect(
    pos=(WIDTH // 2 +180, 200),
    frames=effect_frames,
    frame_interval=5   # เร็ว/ช้า ปรับได้
)

ai_atk_effect = Effect(
    pos=(WIDTH // 2 - 850, 200),
    frames=effect_frames,
    frame_interval=5   # เร็ว/ช้า ปรับได้
)

# ฟังก์ชันหลักของเกม
def main():
    """
    วนลูปหลักของเกม รอการกดปุ่มและวาดกราฟิกทั้งหมด
    """
    gs = GameState()    # สร้างสถานะเกมใหม่
    # สร้างปุ่ม reroll และ confirm
    btn_reroll = pygame.Rect(WIDTH//2-220, 700, 180, 52)
    btn_confirm = pygame.Rect(WIDTH//2+20, 700, 200, 52)
    running = True

    # โหลดและปรับขนาดรูป
    gil_af_img = pygame.transform.smoothscale(Gil_AF, (400, 500))
    gil_af_rect = gil_af_img.get_rect()
    gil_af_rect.midtop = (WIDTH // 2 + 500, 300)

    saber_af_img = pygame.transform.smoothscale(Saber_AF, (400, 500))
    saber_af_rect = saber_af_img.get_rect()
    saber_af_rect.midtop = (WIDTH // 2 - 500, 300)

    # --- เก็บ HPเดิม สำหรับแสดงดาเมจเลือดลด ---
    prev_player_hp = gs.player_hp
    prev_ai_hp = gs.ai_hp

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # ออกจากลูป ถ้าปิดหน้าต่าง
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False  # ออกจากลูป ถ้ากด ESC
                if gs.game_over and event.key == pygame.K_r:
                    gs.reset()      # รีเซ็ตถ้าเกมจบและกด R
                    prev_player_hp = gs.player_hp
                    prev_ai_hp = gs.ai_hp
            if gs.game_over or event.type != pygame.MOUSEBUTTONDOWN:
                continue  # ถ้าเกมจบ หรือไม่ใช่การคลิกเมาส์ ข้ามไป

            mx, my = pygame.mouse.get_pos()  # ตำแหน่งเมาส์
            need = 3 if gs.turn == "player" else 2  # จำนวนลูกเต๋าที่ต้องเลือกในรอบนั้น

            if event.button == 1:  # คลิกซ้าย
                hi = dice_index_at(mx, my)
                if hi is not None:
                    # เลือก/ยกเลิกเลือก ลูกเต๋า (toggle)
                    if gs.picked[hi]:
                        gs.picked[hi] = False
                    elif sum(gs.picked) < need:
                        gs.picked[hi] = True
                elif btn_reroll.collidepoint(mx, my):
                    gs.reroll()  # คลิกปุ่ม reroll
                elif btn_confirm.collidepoint(mx, my) and sum(gs.picked) == need:
                    # --- ก่อน handle_confirm เก็บ HP เดิมไว้ ---
                    old_player_hp = gs.player_hp
                    old_ai_hp = gs.ai_hp

                    atk_round = gs.turn == "player" 

                    gs.handle_confirm()  # คลิกปุ่มยืนยันในขณะที่เลือกครบ

                    if atk_round:
                        player_atk_effect.play()
                    else:
                        ai_atk_effect.play()

                    # --- หลัง confirm เช็ค blood drop ---
                    # หาก HP ลด ให้สร้างข้อความแสดงเลือดลด ลอยขึ้น (FloatingDamage)
                    if gs.player_hp < old_player_hp:
                        dmg = old_player_hp - gs.player_hp
                        # สุ่มตำแหน่งแถบ HP ผู้เล่นด้านซ้าย
                        f_damage.spawn(
                            f"-{dmg}",
                            PLAYER_ATK,
                            (140, 72)
                        )
                    if gs.ai_hp < old_ai_hp:
                        dmg = old_ai_hp - gs.ai_hp
                        # สุ่มตำแหน่งแถบ HP AI ด้านขวา
                        f_damage.spawn(
                            f"-{dmg}",
                            AI_COLOR,
                            (WIDTH - 140, 72)
                        )
            elif event.button == 3:  # คลิกขวา = toggle reroll ลูกเต๋า
                hi = dice_index_at(mx, my)
                if hi is not None:
                    gs.reroll_sel[hi] = not gs.reroll_sel[hi]

        # ----- ส่วนแสดงผลกราฟิก -----
        screen.fill(BG)
        draw_text(screen, "Dice Battle", (WIDTH // 2, 16), TEXT, font_title, anchor="midtop")
        draw_text(screen, f"ผู้เล่น HP: {max(0, gs.player_hp)}", (48, 96), PLAYER_ATK)
        draw_text(screen, f"AI HP: {max(0, gs.ai_hp)}", (WIDTH - 48, 96), AI_COLOR, anchor="topright")
       

        # --- อัปเดตและวาดเอฟเฟกต์เลือดลด ---
        f_damage.update()
        f_damage.draw(screen, font)

        if not gs.game_over:
            # วาดรูปตัวละครก่อน
            screen.blit(gil_af_img, gil_af_rect)
            screen.blit(saber_af_img, saber_af_rect)

            # วาดเอฟเฟกต์ attack เหนือรูปตัวละคร
            player_atk_effect.update()
            ai_atk_effect.update()
            player_atk_effect.draw(screen)
            ai_atk_effect.draw(screen)
        else:           
            player_atk_effect.update()
            ai_atk_effect.update()
            player_atk_effect.draw(screen)
            ai_atk_effect.draw(screen)


        if not gs.game_over:           
            atk_round = gs.turn == "player"    # True ถ้าผู้เล่นโจมตี
            need = 3 if atk_round else 2
            # ข้อมูลแถบบนสำหรับรอบปัจจุบัน
            draw_text(
                screen,
                f"รอบ{'โจมตี — เลือก 3 ลูก' if atk_round else 'ป้องกัน — เลือก 2 ลูก'} "
                f"(คลิกซ้ายเลือกโจมตี | ขวาเลือก Reroll)",
                (WIDTH // 2, 132),
                MUTED,
                font_small,
                anchor="midtop",
            )          
            # วาดแถวลูกเต๋า AI (ดูอย่างเดียว)
            draw_dice_row_ai(
                screen,
                gs.ai_dice,
                250,
                "",
                AI_COLOR,
            )
            draw_text(
                screen,
                f"ลูก AI ({'ป้องกัน' if atk_round else 'โจมตี'}) — ดูอย่างเดียว",
                (1300, 200),
                AI_COLOR,
                font_small,
                anchor="midbottom"
            )
            # วาดแถวลูกเต๋าผู้เล่น
            draw_dice_row_player(
                screen,
                gs.player_dice,
                250,
                "",
                PLAYER_ATK if atk_round else PLAYER_DEF,
                gs.picked,
                gs.reroll_sel,
                atk_round,
            )
            draw_text(
                screen,
                f"ลูกผู้เล่น— เลือก {need} ลูกเป็น{'โจมตี' if atk_round else 'ป้องกัน'}",
                (200, 200),
                PLAYER_ATK,
                font_small,
                anchor="midbottom"
            )
            # ข้อมูลเลือก/คงเหลือ reroll ที่แถบล่าง
            draw_text(
                screen,
                f"เลือกแล้ว {sum(gs.picked)}/{need}  |  Reroll เหลือ {gs.reroll_left}",
                (WIDTH // 2, 392),
                ACCENT,
                font_small,
                anchor="midtop",
            )
            # วาดปุ่ม reroll และยืนยัน
            pygame.draw.rect(screen, BTN_REROLL, btn_reroll, border_radius=10)
            pygame.draw.rect(screen, (200, 200, 200), btn_reroll, 2, border_radius=10)
            draw_text(screen, "Reroll", btn_reroll.center, TEXT, font, anchor="center")
            pygame.draw.rect(screen, BTN_CONFIRM, btn_confirm, border_radius=10)
            pygame.draw.rect(screen, (200, 200, 200), btn_confirm, 2, border_radius=10)
            draw_text(screen, "ยืนยัน", btn_confirm.center, TEXT, font, anchor="center")
            # แสดงผล preview คะแนนโจมตี/ป้องกัน
            pu = sum(d for d, p in zip(gs.player_dice, gs.picked) if p)
            ai_sum = gs.ai_best(gs.ai_dice, 2 if atk_round else 3)
            preview = (
                f"โจมตีผู้เล่น {pu}  vs  ป้องกัน AI {ai_sum}"
                if atk_round
                else f"โจมตี AI {ai_sum}+{gs.ai_attack_bonus}  vs  ป้องกันผู้เล่น {pu}"
            )
            draw_text(screen, preview, (WIDTH // 2, 500), MUTED, font_small, anchor="midtop")
        else:
            # แสดงผลเมื่อเกมจบ
            draw_text(
                screen,
                "คุณชนะ!" if gs.winner == "player" else "AI ชนะ!",
                (WIDTH // 2, 248),
                ACCENT,
                font_title,
                anchor="center",
            )
            draw_text(screen, "กด R เล่นใหม่  |  ESC ออก", (WIDTH // 2, 312), MUTED, font_small, anchor="midtop")

        pygame.display.flip()     # อัปเดตจอ
        clock.tick(FPS)          # หน่วงเวลาให้ตาม FPS

    pygame.quit()
    sys.exit(0)

# เลือกให้รัน main() เมื่อรันไฟล์นี้โดยตรง
if __name__ == "__main__":
    main()
