import math

class Ease():
    @classmethod
    def liner(self, start, end, progress):
        return (end - start) * progress + start
    @classmethod
    def inSine(self, start, end, progress):
        return (end - start) * (1 - math.cos(progress * math.pi / 2)) + start
    @classmethod
    def inQuad(self, start, end, progress):
        return (end - start) * (progress ** 2) + start
    @classmethod
    def inQuad_inverse(self, start, end, value):
        progress = math.sqrt(max((value - start) / (end - start), 0))
        return progress
    @classmethod
    def InExpo(self, start, end, progress):
        return  start if progress == 0 else (end - start) * (pow(2, 10 * progress - 10)) + start