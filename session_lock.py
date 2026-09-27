"""
Cross-platform screen/session lock.
Each OS has its own native lock mechanism — we just call it. No CV or DB
logic lives here on purpose, so you can test this file completely on its
own with: python -c "from session_lock import lock_session; lock_session()"
"""
import platform
import subprocess


def lock_session():
    system = platform.system()
    try:
        if system == "Windows":
            import ctypes
            ctypes.windll.user32.LockWorkStation()

        elif system == "Linux":
            # works on most desktop environments (GNOME, KDE, XFCE via loginctl)
            subprocess.run(["loginctl", "lock-session"], check=False)

        elif system == "Darwin":
            # simulates Control+Command+Q, macOS's built-in lock shortcut
            subprocess.run(
                ["osascript", "-e",
                 'tell application "System Events" to keystroke "q" '
                 'using {control down, command down}'],
                check=False,
            )
        else:
            print(f"[!] Don't know how to lock session on {system}")

    except Exception as e:
        print(f"[!] Lock command failed: {e}")
