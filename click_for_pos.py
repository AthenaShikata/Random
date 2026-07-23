from pynput import mouse
import threading

stop_event = threading.Event()

def on_click(x, y, button, pressed):
    if pressed:
        print(f'{button} clicked at ({x}, {y})')

print("Click anywhere to get coordinates. Press Ctrl+C to stop.\n")

with mouse.Listener(on_click=on_click) as listener:
    try:
        while listener.running:
            stop_event.wait(timeout=0.1)
    except KeyboardInterrupt:
        print("\nStopped.")
        listener.stop()