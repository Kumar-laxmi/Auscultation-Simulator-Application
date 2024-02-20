#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    try:
        from rpi_lcd import LCD
        import subprocess
        lcd = LCD()
        ip_addr = str(subprocess.check_output(['hostname', '-I'])).split(' ')[0].replace("b'", "")
        lcd.clear()
        lcd.text("Server Running on", 1)
        lcd.text(ip_addr, 2)
        main()
    except:
        main()
