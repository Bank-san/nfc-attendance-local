from PyQt6.QtCore import QThread, pyqtSignal
from smartcard.System import readers
from smartcard.util import toHexString
import time

class NFCWorker(QThread):
    signal = pyqtSignal(str)

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
                    self.signal.emit(uid)
                else:
                    self.signal.emit("UID取得失敗")

                time.sleep(1)
                connection.disconnect()
            except Exception as e:
                self.signal.emit(f"エラー: {e}")
                time.sleep(0.5)