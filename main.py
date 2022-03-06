from pystray import Icon, MenuItem
from PIL import Image
from threading import Thread
from time import sleep
from get_config import get_config
from get_path import get_path


class TrayInstance:
    def __init__(self):
        self.WORK_MIN, self.SHORT_BREAK_MIN, self.LONG_BREAK_MIN, self.SESSIONS, self.AUTO_BREAK, self.AUTO_WORK \
            = get_config()
        self.pomodoro_count = 0
        self.cycle_count = 0
        self.status = False
        self.thread = None

        self.icon_image = Image.open(get_path('icon.png'))
        self.menu = (MenuItem(lambda text: 'Start Session' if not self.status else 'Continue Session',
                              self.toggle_timer),
                     MenuItem(lambda text: 'Stop Session' if self.thread else 'Reset Session', self.stop_timer),
                     MenuItem('Exit', self.exit_program))
        self.icon = Icon('Simple Pomodoro', self.icon_image, 'Simple Pomodoro\nby pinterbanget', self.menu)
        self.icon.run()

    def toggle_timer(self):
        self.status = True

        if self.thread:
            self.status = False
            self.icon.notify(f'Your session has been skipped.',
                             f'{"Break" if self.cycle_count % 2 else "Work"} Session Skipped')
            sleep(1)
            self.status = True

        else:
            if self.cycle_count % 2:
                if self.pomodoro_count < self.SESSIONS:
                    self.icon.notify(f'Your break session ({self.SHORT_BREAK_MIN} min) has started.',
                                     f'Break Session Started')
                    self.thread = Thread(target=self.pomodoro_timer, args=(self.SHORT_BREAK_MIN,), daemon=True)
                    self.thread.start()

                else:
                    self.icon.notify(F'Your long break session ({self.LONG_BREAK_MIN} min) has started. Have a rest!',
                                     f'Long Break Session Started')
                    self.thread = Thread(target=self.pomodoro_timer, args=(self.LONG_BREAK_MIN,), daemon=True)
                    self.thread.start()
                    self.pomodoro_count = 0
                    self.cycle_count = -1

            else:
                self.icon.notify(f'Your work session ({self.WORK_MIN} min) has started.',
                                 f'Work Session Started ({self.pomodoro_count + 1}/{self.SESSIONS})')
                self.thread = Thread(target=self.pomodoro_timer, args=(self.WORK_MIN,), daemon=True)
                self.thread.start()

        self.icon.update_menu()

    def stop_timer(self):
        if self.thread:
            self.status = False
            self.icon.notify('Pomodoro session has been stopped.', 'Pomodoro Session Stopped')
            self.icon.title = 'Simple Pomodoro\nSession stopped'
            if self.cycle_count % 2:
                self.pomodoro_count -= 1
            self.cycle_count -= 1
        else:
            self.pomodoro_count = 0
            self.cycle_count = 0
            self.icon.notify('Pomodoro session has been reset.', 'Pomodoro Session Reset')
            self.icon.title = 'Simple Pomodoro\nSession reset'

    def pomodoro_timer(self, time_slot):
        count = time_slot * 60
        while count > 0 and self.status:
            self.icon.title = f'Simple Pomodoro\n' \
                              f'{self.pomodoro_count}/{self.SESSIONS} completed\n' \
                              f'[{count // 60}:{count % 60 if count % 60 > 9 else "0" + str(count % 60)}] ' \
                              f'{"Break time" if self.cycle_count % 2 else f"Work time"} '
            count -= 1
            sleep(1)

        self.cycle_count += 1

        if self.cycle_count % 2:
            self.pomodoro_count += 1

        if self.status:
            if self.cycle_count % 2:
                if self.AUTO_BREAK:
                    self.toggle_timer()
                else:
                    self.icon.notify('Your work session is over. Have a break!',
                                     f'Work Session {self.pomodoro_count}/{self.SESSIONS} Completed!')
            else:
                if self.AUTO_WORK:
                    self.toggle_timer()
                else:
                    self.icon.notify('Your break session is over. Continue the timer when you\'re ready.',
                                     f'Break Session Over')

        self.icon.title = f'Simple Pomodoro\n' \
                          f'{self.pomodoro_count}/{self.SESSIONS} completed\n' \
                          f'Next: {"break" if self.cycle_count % 2 else "work"} sess.'
        self.thread = None
        self.icon.update_menu()

    def exit_program(self):
        self.icon.visible = False
        self.icon.stop()


if __name__ == '__main__':
    app = TrayInstance()
