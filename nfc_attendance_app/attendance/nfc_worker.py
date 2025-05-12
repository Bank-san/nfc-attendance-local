from PyQt6.QtCore import QThread, pyqtSignal
from smartcard.System import readers
from smartcard.util import toHexString
from datetime import datetime, timedelta
import time

class NFCWorker(QThread):
    signal = pyqtSignal(str)

    def __init__(self, wait_seconds="30"):
        super().__init__()
        self.last_uid = None
        self.last_read_time = None
        self.last_time = None
        self.wait_seconds = wait_seconds

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
                    if uid == self.last_uid and self.last_time and now - self.last_time < timedelta(seconds=self.wait_seconds):
                        # 同じカードで短時間ならスキップ
                        time.sleep(0.5)
                        continue

                    self.last_uid = uid
                    self.last_time = now

                    self.signal.emit(uid)
                else:
                    self.signal.emit("カードをかざしてください")

                time.sleep(0.5)
                connection.disconnect()

            except Exception as e:
                # スマートカード未挿入などの場合
                self.signal.emit("カードをかざしてください")
                time.sleep(0.5)
