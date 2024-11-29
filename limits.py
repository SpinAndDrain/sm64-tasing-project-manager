import time


def now():
    return int(time.time() * 1000)


class RequestLimiter():
    def __init__(self, max_requests, time_recover_ms, func_is_privileged = None):
        self._reg = {}
        self._mr = max_requests
        self._tr = time_recover_ms
        self._f = func_is_privileged
    
    def can_request_now(self, user, amount):
        if self._f and self._f(user):
            return True
        if user not in self._reg:
            return amount <= self._mr
        if self._reg[user]["n"] + amount <= self._mr:
            return True
        if abs(now() - self._reg[user]["t"]) >= self._tr:
            return True
        return False
    
    def acknowledge(self, user, amount):
        if self._f and self._f(user):
            return
        if (user not in self._reg) or (abs(now() - self._reg[user]["t"]) >= self._tr):
            self._reg[user] = { "n": amount, "t": now() }
            return
        self._reg[user]["n"] += amount
