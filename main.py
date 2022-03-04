from pystray import Icon, MenuItem
from PIL import Image
from get_config import get_config
from threading import Thread
from time import sleep


class TrayInstance:
    def __init__(self):
        self.WORK_MIN, self.SHORT_BREAK_MIN, self.LONG_BREAK_MIN, self.SESSIONS, self.AUTO_BREAK, self.AUTO_WORK \
            = get_config()
        self.pomodoro_count = 1
        self.status = False
        self.is_work = False
        self.thread = None

        self.icon_image = Image.open('icon.png')
        self.menu = (MenuItem(lambda text: 'Start Session' if not self.status else 'Continue Session',
                              self.toggle_timer),
                     MenuItem(lambda text: 'Stop Session' if self.status else 'Reset Session', self.stop_timer),
                     MenuItem('Exit', self.exit_program))
        self.icon = Icon('Simple Pomodoro', self.icon_image, 'Simple Pomodoro', self.menu)
        self.icon.run()

    def toggle_timer(self):
        self.status = True

        if self.is_work:
            self.is_work = False
            if self.pomodoro_count <= self.SESSIONS:
                self.icon.notify(f'Your break session ({self.SHORT_BREAK_MIN} min) has started.',
                                 f'Break Session Started ({self.pomodoro_count - 1}/{self.SESSIONS})')
                self.thread = Thread(target=self.pomodoro_timer, args=(self.SHORT_BREAK_MIN,), daemon=True)
                self.thread.start()

            else:
                self.icon.notify(F'Your long break session ({self.LONG_BREAK_MIN} min) has started. Have a rest!',
                                 f'Long Break Session Started')
                self.thread = Thread(target=self.pomodoro_timer, args=(self.LONG_BREAK_MIN,), daemon=True)
                self.thread.start()
                self.pomodoro_count -= self.SESSIONS
                # self.status = False

        else:
            self.is_work = True
            self.icon.notify(f'Your work session ({self.WORK_MIN} min) has started.',
                             f'Work Session Started ({self.pomodoro_count}/{self.SESSIONS})')
            self.thread = Thread(target=self.pomodoro_timer, args=(self.WORK_MIN,), daemon=True)
            self.thread.start()

        self.icon.update_menu()

    def stop_timer(self):
        self.is_work = False
        if self.status:
            self.status = False
            self.icon.notify('Pomodoro session has been stopped.', 'Pomodoro Session Stopped')
            self.icon.title = 'Simple Pomodoro\nSession stopped'
        else:
            self.pomodoro_count = 1
            self.icon.notify('Pomodoro session has been reset.', 'Pomodoro Session Reset')
            self.icon.title = 'Simple Pomodoro\nSession reset'

    def pomodoro_timer(self, time_slot):
        count = time_slot * 60
        while count > 0 and self.status:
            self.icon.title = f'Simple Pomodoro\n' \
                              f'{"Work" if self.is_work else "Break"} time ({self.pomodoro_count}/{self.SESSIONS})\n' \
                              f'{count // 60}:{count % 60 if count % 60 > 9 else "0" + str(count % 60)}'
            count -= 1
            sleep(1)

        if self.status:
            if self.is_work:
                if self.AUTO_BREAK:
                    self.toggle_timer()
                else:
                    self.icon.notify('Your work session is over. Have a break!',
                                     f'Work Session {self.pomodoro_count}/{self.SESSIONS} Completed!')
                self.pomodoro_count += 1

            else:
                if self.AUTO_WORK:
                    self.toggle_timer()
                else:
                    self.icon.notify('Your break session is over. Continue the timer when you\'re ready.',
                                     f'Break Session {self.pomodoro_count}/{self.SESSIONS} Over')

        self.icon.title = f'Simple Pomodoro\n{self.pomodoro_count - 1} ' \
                          f'session{"s" if self.pomodoro_count - 1 != 1 else ""} finished\n' \
                          f'Upcoming: {"break" if self.is_work else "work"} session'

    def exit_program(self):
        self.icon.visible = False
        self.icon.stop()


if __name__ == '__main__':
    app = TrayInstance()
