import pygame


class Effect:
    """
    คลาส Effect สำหรับจัดการเอฟเฟกต์ภาพเคลื่อนไหวแบบเฟรม    
    """
    def __init__(self, pos, frames=None, frame_interval=3):
        self.pos = pos
        self.frames = frames if frames else []
        self.frame_interval = frame_interval
        self.current = 0
        self.timer = 0
        self.playing = False

    def play(self):
        """
        เริ่มต้นหรือเล่น effect ใหม่อีกครั้งจากเฟรมแรก
        """
        self.playing = True
        self.current = 0
        self.timer = 0

    def update(self):
        """
        ต้องเรียกใช้งานทุก frame เพื่ออัปเดตสถานะของ effect:
        - ถ้า playing == True ให้นับ timer
        - เมื่อครบ frame_interval จะเปลี่ยนเป็นเฟรมถัดไป
        - หากเล่นจนถึงเฟรมสุดท้ายจะหยุด (playing=False)
        """
        if self.playing:
            self.timer += 1
            if self.timer >= self.frame_interval:
                self.timer = 0
                self.current += 1
                if self.current >= len(self.frames):
                    self.playing = False
                    self.current = 0

    def draw(self, surf):
        """
        แสดงภาพเฟรมปัจจุบันของ effect บนพื้นผิว surf (เช่นหน้าจอ)
        """
        if self.playing and self.frames:
            img = self.frames[self.current]
            rect = img.get_rect()
            rect.topleft = self.pos
            surf.blit(img, rect)