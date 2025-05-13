from PyQt6.QtCore import QThread, pyqtSignal
from smartcard.System import readers
from smartcard.util import toHexString
from datetime import datetime, timedelta
import time

class NFCWorker(QThread):
    signal = pyqtSignal(str)

    def __init__(self, wait_seconds=0, mode="attendance"):
        super().__init__()
        self.wait_seconds = wait_seconds
        self.mode = mode  # "attendance" or "registration"
        self.last_uid = None
        self.last_time = None
        self.card_present = False

    def run(self):
        r = readers()
        if not r:
            self.signal.emit("⚠️ NFCリーダーが見つかりません")
            return

        reader = r[0]
        connection = reader.createConnection()

        while True:
            try:
                connection.connect()
                cmd = [0xff, 0xca, 0x00, 0x00, 0x00]
                data, sw1, sw2 = connection.transmit(cmd)

                if sw1 == 0x90 and sw2 == 0x00:
                    uid = toHexString(data)
                    now = datetime.now()

                    if uid == self.last_uid:
                        if not self.card_present:
                            if self.wait_seconds == 0 or not self.last_time or now - self.last_time >= timedelta(seconds=self.wait_seconds):
                                self.signal.emit(uid)
                                self.last_time = now
                                self.card_present = True
                    else:
                        self.signal.emit(uid)
                        self.last_uid = uid
                        self.last_time = now
                        self.card_present = True

                else:
                    self.card_present = False
                    self.last_uid = None
                    self.signal.emit("カードをかざしてください")

                time.sleep(0.5)
                connection.disconnect()

            except Exception:
                self.card_present = False
                self.last_uid = None
                self.signal.emit("カードをかざしてください")
                time.sleep(0.5)
