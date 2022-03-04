def get_config(file: str = 'config.txt') -> list:
    """
    Fetches user configuration from the config.txt file.
    Returns a list of integers containing values needed for the Pomodoro timer.
    """
    default_values = [25, 5, 20, 4, 0, 1]
    time_config = []
    try:
        with open(file, encoding='utf8') as f:
            for line in f.readlines():
                if len(time_config) == 6:
                    return time_config
                try:
                    time_config.append(int(line.strip().split(': ')[1].split(' ')[0]))
                except ValueError:
                    time_config.append(default_values[len(time_config)])

        return time_config
    except FileNotFoundError:
        return default_values



