#!/usr/bin/env python3
# pylint: disable=import-error

"""
GPIO 과제
- gpiozero 라이브러리 사용

UART 과제
- pyserial 라이브러리 사용
- UART 통신: 115200 bps, 8N1, 플로우 제어 없음
- TXD3/RXD3을 활용
"""

import sys
import time

from gpiozero import LED, Button
from serial import Serial


def blink_led() -> None:
    """
    [문제 1] 18번 핀에 연결된 LED를 1초 간격으로 ON/OFF를 10번 반복
    - gpiozero.LED 사용
    - 종료시 LED는 OFF 상태
    """
    # TODO: blink_led 구현
    for _ in range(10):
        LED(18).on()
        time.sleep(1)
        LED(18).off()
        time.sleep(1)

    


def check_to_input_button() -> None:
    """
    [문제 2] 18번 핀 버튼 입력을 받아서
      - 눌렸을 때: 'pressed'
      - 뗐을 때:   'released'
    를 출력한다.
    - polling 방식으로 구현할 것.
    - 버튼 입력을 10번 받았으면 종료.
    """
    # TODO: check_to_input_button 구현
    btn = Button(18, pull_up=True)
    btn_prev = btn.is_pressed
    count = 0 
    while count < 10:
        curr = btn.is_pressed
        if curr != btn_prev:
            if curr:
                print("pressed")
                count += 1
            else:
                print("released")
        btn_prev = curr
        time.sleep(0.01)
    return


def blink_led_through_button() -> None:
    """
    [문제 3]
    - 12번: LED 출력
    - 13번: Button 입력
    - 버튼이 눌려 있는 동안에만 LED가 0.5초 간격으로 깜빡인다.
    - 버튼이 10번 눌려졌으면 종료.
    - 종료시 LED는 OFF 상태
    """
    # TODO: blink_led_through_button 구현
    led = LED(12)
    btn = Button(13, pull_up=True)
    prev = btn.is_pressed
    count = 0
    while count < 10:
        if btn.is_pressed:
            led.toggle()
            time.sleep(0.5)
        else:
            led.off()
        if btn.is_pressed and not prev:
            count += 1
    led.off()
    return




def transmit_msg() -> None:
    """
    [문제 1] UART3로 "Hello World! {i}" 문자열을 1초마다 전송
    - 총 10번 전송 후 종료
    - 개행을 붙여 전송 (수신/테스트 편의)
    """
    # TODO: blink_led_through_button 구현
    ser = Serial('/dev/ttyAMA3', baudrate=115200, timeout=1.0)
    for i in range(10):
        ser.write((f"Hello World! {i}\r\n").encode())
        time.sleep(1)
    ser.close()
    return



def receive_msg() -> None:
    """
    [문제 2] UART3에서 줄 단위로 읽어 화면에 출력.
    - 'exit' (대소문자 무시) 라인을 수신하면 함수 종료
    """
    # TODO: blink_led_through_button 구현
    ser = Serial('/dev/ttyAMA3', baudrate=115200, timeout=1.0)
    time.sleep(2)
    buf = bytearray()
    try:
        while True:
            lines = []
            # prefer readline if available
            if hasattr(ser, "readline"):
                raw = ser.readline()
                if not raw:
                    # no data right now
                    time.sleep(0.01)
                    continue
                try:
                    text = raw.decode()
                except Exception:
                    text = str(raw)
                # readline may return multiple lines if the fake provides them; split safely
                parts = text.splitlines()
                for p in parts:
                    lines.append(p)
            else:
                # fallback: accumulate bytes and split on '\n'
                data = b""
                if hasattr(ser, "read_all"):
                    data = ser.read_all()
                elif hasattr(ser, "read_until"):
                    data = ser.read_until(b"\n")
                elif hasattr(ser, "read"):
                    # try to read whatever is available
                    try:
                        if hasattr(ser, "in_waiting"):
                            n = getattr(ser, "in_waiting", 0)
                            data = ser.read(n or 1)
                        else:
                            data = ser.read(1)
                    except Exception:
                        data = ser.read(1)
                else:
                    # nothing to read, wait a bit
                    time.sleep(0.01)
                    continue

                if not data:
                    time.sleep(0.01)
                    continue

                buf.extend(data)
                while True:
                    if b"\n" in buf:
                        idx = buf.index(b"\n")
                        line_bytes = bytes(buf[:idx])
                        del buf[:idx + 1]
                        try:
                            lines.append(line_bytes.decode())
                        except Exception:
                            lines.append(str(line_bytes))
                    else:
                        break

            # process complete lines
            for l in lines:
                s = l.strip()
                if s:
                    print(s)
                if s.lower() == "exit":
                    ser.close()
                    return
    finally:
        try:
            ser.close()
        except Exception:
            pass


if __name__ == "__main__":
    blink_led()
    check_to_input_button()
    blink_led_through_button()

    transmit_msg()
    receive_msg()
